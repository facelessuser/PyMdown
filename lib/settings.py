#!/usr/bin/env python
"""
PyMdown Settings

Manage Settings

Licensed under MIT
Copyright (c) 2014 Isaac Muse <isaacmuse@gmail.com>
"""
from __future__ import unicode_literals
import json
import re
import codecs
import traceback
import sys
from copy import deepcopy
from os.path import dirname, abspath, exists, normpath, expanduser
from os.path import isfile, isdir, splitext, join, basename
from . import resources as res
from .logger import Logger
import yaml
from .file_strip.json import sanitize_json
from .resources import resource_exists, splitenc, unpack_user_files, is_absolute
import markdown.extensions.codehilite as codehilite
try:
    from pygments.styles import get_style_by_name
    PYGMENTS_AVAILABLE = codehilite.pygments
except:
    PYGMENTS_AVAILABLE = False

PY3 = sys.version_info >= (3, 0)

if PY3:
    unicode_string = str
    string_type = str
else:
    unicode_string = unicode  # flake8: noqa
    string_type = basestring


PAGE_KEYS = ('destination', 'basepath', 'references', 'include.js', 'include.css', 'include')

CRITIC_IGNORE = 0
CRITIC_ACCEPT = 1
CRITIC_REJECT = 2
CRITIC_VIEW = 4
CRITIC_DUMP = 8


class Settings(object):
    def __init__(
        self, settings_path=None, stream=False,
        batch=False, critic=CRITIC_IGNORE,
        plain=False, preview=False, encoding='utf-8', output_encoding='utf-8',
        force_stdout=False, force_no_template=False,
        clean=False
    ):
        """ Initialize """
        self.critic = critic
        self.plain = plain
        self.batch = batch
        self.encoding = encoding
        self.output_encoding = output_encoding
        self.preview = preview
        self.is_stream = stream
        self.pygments_noclasses = False
        self.force_stdout = force_stdout
        self.clean = clean
        self.force_no_template = force_no_template
        self.settings = {
            "page": {
                "destination": None,
                "basepath": None,
                "references": [],
                "include": [],
                "meta": {}
            },
            "settings": {}
        }

        # Use default file if one was not provided
        if settings_path is None:
            settings_path = "pymdown.cfg"

        # Get the settings if available
        unpack_user_files()
        self.read_settings(settings_path)

    def read_settings(self, settings_path):
        """
        Get the settings and add absolutepath
        extention if a preview is planned.
        Unpack the settings file if needed.
        """

        settings = None

        # Unpack default settings file if needed
        if not exists(settings_path):
            text = res.load_text_resource(res.DEFAULT_SETTINGS, internal=True)
            try:
                with codecs.open(settings_path, "w", encoding="utf-8") as f:
                    f.write(text)
            except:
                Logger.error(traceback.format_exc())

        # Try and read settings file
        try:
            with codecs.open(settings_path, "r", encoding='utf-8') as f:
                contents = f.read()
                try:
                    settings = json.loads(sanitize_json(contents))
                except:
                    settings = yaml.load(contents)
        except:
            Logger.error(traceback.format_exc())

        if settings is None:
            settings = {}

        self.settings["settings"] = settings

    def get(self, file_name, output, basepath, frontmatter=None):
        """ Get the complete settings object for the given file """
        self.file_name = file_name
        settings = deepcopy(self.settings)
        settings["page"]["destination"] = self.resolve_output(output)
        settings["page"]["basepath"] = self.resolve_base_path(basepath)
        if frontmatter is not None:
            self.apply_frontmatter(frontmatter, settings)
        if settings['page']['destination'] is not None:
            self.destination = abspath(settings['page']['destination'])
        else:
            self.destination = None
        if self.force_stdout:
            settings["page"]["destination"] = None
        if self.force_no_template:
            settings['settings']['template'] = None
        self.post_process_settings(settings)
        return settings

    def resolve_output(self, out_name):
        """ Get the path to output the file. """

        critic_enabled = self.critic & (CRITIC_ACCEPT | CRITIC_REJECT | CRITIC_VIEW)
        output = None
        if out_name is not None:
            out_name = expanduser(out_name)
        if not self.batch:
            if out_name is not None:
                name = abspath(out_name)
                if isdir(out_name):
                    Logger.error("'%s' is a directory!" % name)
                elif exists(dirname(name)):
                    output = name
                else:
                    Logger.error("'%s' directory does not exist!" % name)
        else:
            name = abspath(self.file_name)
            if self.critic & CRITIC_DUMP and critic_enabled:
                if self.critic & CRITIC_REJECT:
                    label = ".rejected"
                elif self.critic & CRITIC_ACCEPT:
                    label = ".accepted"
                else:
                    label = '.view'
                base, ext = splitext(abspath(self.file_name))
                output = join(name, "%s%s%s" % (base, label, ext))
            else:
                output = join(name, "%s.html" % splitext(abspath(self.file_name))[0])

        return output

    def resolve_base_path(self, basepath):
        """ Get the base path to use when resolving basepath paths if possible """
        if basepath is not None:
            basepath = expanduser(basepath)
        if basepath is not None and exists(basepath):
            # A valid path was fed in
            path = basepath
            basepath = dirname(abspath(path)) if isfile(path) else abspath(path)
        elif not self.is_stream:
            # Use the current file path
            basepath = dirname(abspath(self.file_name))
        else:
            # Okay, there is no way to tell the orign.
            # We are probably a stream that has no specified
            # physical location.
            basepath = None

        return basepath

    def resolve_meta_path(self, target, basepath):
        """
        Resolve the path returned in the meta data.
        1. See if path is defined as absolute and if so see
           if it exists
        2. If relative, use the file's basepath (default its physical directory
           if available) if the file
           can be found
        """
        if target is not None:
            target = expanduser(target)
            if not is_absolute(target):
                new_target = None
                if basepath is not None:
                    temp = join(basepath, target)
                    if exists(temp):
                        new_target = temp
                target = new_target
            elif not exists(target):
                target = None
        return target

    def process_settings_path(self, pth, base):
        target, encoding = splitenc(pth)

        file_path = self.resolve_meta_path(
            pth,
            base
        )
        if file_path is None or not isfile(file_path):
            file_path = None
        else:
            file_path = normpath(file_path)
        return file_path + ';' + encoding if file_path is not None else None

    def apply_frontmatter(self, frontmatter, settings):
        """ Apply front matter to settings object etc. """

        # Handle basepath first
        if "basepath" in frontmatter:
            value = frontmatter["basepath"]
            settings["page"]["basepath"] = self.resolve_base_path(value)
            del frontmatter["basepath"]
        base = settings["page"]["basepath"]

        # The destination/output location and name
        if "destination" in frontmatter:
            value = frontmatter['destination']
            file_name = self.resolve_meta_path(dirname(unicode_string(value)), base)
            if file_name is not None and isdir(file_name):
                value = normpath(join(file_name, basename(value)))
                if exists(value) and isdir(value):
                    value = None
            else:
                value = None
            if value is not None:
                settings["page"]["destination"] = value
            del frontmatter['destination']
        destination = settings["page"]["destination"]

        css = []
        js = []

        # Resolve all frontmatter items
        for key, value in frontmatter.items():

            # Handle PyMdown settings
            if key == "settings" and isinstance(value, dict):
                for subkey, subvalue in value.items():
                    # Html template
                    if subkey == "template":
                        org_pth = unicode_string(subvalue)
                        new_pth = self.process_settings_path(org_pth, base)
                        settings[key][subkey] = new_pth if new_pth is not None else org_pth

                    # Handle optional extention assets
                    elif subkey.startswith('@'):
                        for assetkey, assetvalue in subvalue.items():
                            if assetkey in ('cs', 'js'):
                                items = []
                                for i in assetvalue:
                                    pth = unicode_string(i)
                                    items.append(pth)
                                settings[key][subkey][assetkey] = items
                            else:
                                settings[key][subkey][assetkey] = assetvalue

                    # Javascript and CSS files
                    elif subkey in ("css", "js"):
                        items = []
                        for i in subvalue:
                            pth = unicode_string(i)
                            items.append(pth)
                        settings[key][subkey] = items

                    # All other settings that require no other special handling
                    else:
                        settings[key][subkey] = subvalue

            # Built in frontmatter keys
            elif key in PAGE_KEYS:
                # Included references markdown (footnotes, abbreviations, etc.)
                if key == "references":
                    if not isinstance(value, list):
                        value = [value]
                    refs = []
                    for v in value:
                        pth = unicode_string(v)
                        refs.append(pth)
                    settings["page"][key] = refs

                elif key == "include":
                    if not isinstance(value, list):
                        value = []
                    settings["page"][key] = [unicode_string(v) for v in value if isinstance(v, string_type)]

                elif key in ("include.css", "include.js"):
                    items = []
                    for i in value:
                        pth = unicode_string(i)
                        items.append(pth)
                    if key == 'include.css':
                        css += items
                    else:
                        js += items

            # Everything else is added to meta
            else:
                if isinstance(value, list):
                    value = [unicode_string(v) for v in value]
                else:
                    value = unicode_string(value)
                settings["page"]["meta"][unicode_string(key)] = value

        # Append CSS and JS from built-in keys if any
        if len(css):
            css = settings['settings'].get('css', []) + css
            settings['settings']['css'] = css
        if len(js):
            js = settings['settings'].get('js', []) + js
            settings['settings']['js'] = js


    def set_style(self, extensions, settings):
        """
        Search the extensions for the style to be used and return it.
        If it is not explicitly set, go ahead and insert the default
        style (github).
        """
        style = None

        use_pygments = settings["settings"].get('use_pygments', True)
        if use_pygments and not PYGMENTS_AVAILABLE:
            use_pygments = False
        if use_pygments:
            codehilite.pygments = True
        else:
            codehilite.pygments = False
            settings["settings"]["use_pygments_css"] = False

        count = 0
        for e in extensions:
            # Search for codehilite to see what style is being set.
            if e.get('name', '') == "markdown.extensions.codehilite":
                config = e.get('config', {})

                if bool(config.get('noclasses', False)):
                    settings["settings"]["use_pygments_css"] = False

                css_class = config.get('css_class', None)
                if css_class is not None:
                    settings["settings"]["pygments_class"] = css_class
                else:
                    settings["settings"]["pygments_class"] = "codehilite"

                style = config.get('pygments_style', None)
                if style is None:
                    # Explicitly define a pygment style and store the name
                    # This is to ensure the "noclasses" option always works
                    style = "default"
                else:
                    try:
                        # Check if the desired style exists internally
                        get_style_by_name(style)
                    except:
                        Logger.error("Cannot find style: %s! Falling back to 'default' style." % style)
                        style = "default"
                config['pygments_style'] = style

            count += 1
        settings["settings"]["style"] = style

    def post_process_settings(self, settings):
        """ Process the settings files making needed adjustements """

        path_converter = False
        critic_found = []
        plain_html = []
        empty = []
        extensions = settings["settings"].get("extensions", [])

        # See if we need to handle the appropriate critic from CLI
        # Critic will be appended to end of extension list if CLI requested it.
        critic_mode = "ignore"
        if self.critic & CRITIC_ACCEPT:
            critic_mode = "accept"
        elif self.critic & CRITIC_REJECT:
            critic_mode = "reject"
        elif self.critic & CRITIC_VIEW:
            critic_mode = "view"

        # Track whether:
        #    - module definition name is missing
        #    - absolute paths is enabled,
        #    - Where the critic extension is enabled
        #    - Where the plainhtml plugin is enabled
        # Only add to list for removal if we are overriding them.
        for i in range(0, len(extensions)):
            name = extensions[i].get('name', None)
            if name is None:
                empty.append(i)
            elif name == "pymdown.pathconverter":
                path_converter = True
            elif name == "pymdown.critic" and critic_mode != 'ignore':
                critic_found.append(i)
            elif name == "pymdown.plainhtml" and self.plain:
                plain_html.append(i)

        # Remove plainhtml and critic because CLI is overriding them
        # Also remove empty modules
        indexes = list(set(critic_found + plain_html + empty))
        indexes.sort()
        for index in reversed(indexes):
            del extensions[index]

        preview_path_conversion = settings["settings"].get("preview_path_conversion", "absolute")

        # Ensure previews are using absolute paths or relative paths
        if self.preview:
            # Add pathconverter extension if not already set.
            if not path_converter:
                extensions.append(
                    {
                        "name": "pymdown.pathconverter",
                        "config":{
                            "base_path": "${BASE_PATH}",
                            "relative_path": "${OUTPUT}",
                            "absolute": preview_path_conversion != 'relative'
                        }
                    }
                )
            else:
                # Make sure file output location is the relative ouput location for previews
                for i in range(0, len(extensions)):
                    name = extensions[i].get('name', None)
                    if name == 'pymdown.pathconverter':
                        if "config" not in extensions[i]:
                            extensions[i]['config'] = {}
                        extensions[i]['config']["relative_path"] = "${OUTPUT}"
                        break

        # Add critic to the end since it is most reliable when applied to the end.
        if critic_mode != "ignore":
            extensions.append(
                {
                    "name": "pymdown.critic",
                    "config": {"mode": critic_mode}
                }
            )

        # Append plainhtml.
        # Most reliable when applied to the end. Okay to come after critic.
        if self.plain:
            extensions.append({"name": "pymdown.plainhtml"})

        # Set extensions to its own key
        settings["settings"]["extensions"] = extensions

        # Set style
        self.set_style(extensions, settings)
