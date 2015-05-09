#!/usr/bin/env python
"""
PyMdown Settings

Manage Settings

Licensed under MIT
Copyright (c) 2014 Isaac Muse <isaacmuse@gmail.com>
"""
from __future__ import unicode_literals
from __future__ import absolute_import
import json
import codecs
import traceback
import os.path as path
from copy import deepcopy
from . import util
from . import logger
from . import file_strip as fstrip
from collections import OrderedDict
from .compat import unicode_string, string_type
try:
    from pygments.styles import get_style_by_name
    PYGMENTS_AVAILABLE = True
except:
    PYGMENTS_AVAILABLE = False


class MergeSettings(object):
    """
    Apply front matter to settings object etc.
    PAGE_KEYS: destination, basepath, references,
               include.js', include.css', include
    SETTIGS_KEY: settings
    META_KEYS: all other keys that aren't handled above
    """

    def __init__(self, file_name, is_stream):
        self.file_name = file_name
        self.is_stream = is_stream
        self.base = None
        self.css = []
        self.js = []

    def process_settings_path(self, pth, base):
        """ General method to process paths in settings file """
        target, encoding = util.splitenc(pth)

        file_path = util.resolve_meta_path(
            pth,
            base
        )
        if file_path is None or not path.isfile(file_path):
            file_path = None
        else:
            file_path = path.normpath(file_path)
        return file_path + ';' + encoding if file_path is not None else None

    def merge_basepath(self, frontmatter, settings):
        """ Merge the basepath """
        if "basepath" in frontmatter:
            value = frontmatter["basepath"]
            settings["page"]["basepath"] = util.resolve_base_path(
                value,
                self.file_name,
                is_stream=self.is_stream
            )
            del frontmatter["basepath"]
        self.base = settings["page"]["basepath"]

    def merge_relative_path(self, frontmatter, settings):
        """ Merge the relative path """
        if "relpath" in frontmatter:
            value = frontmatter["relpath"]
            settings["page"]["relpath"] = util.resolve_relative_path(value)
            del self.frontmatter["relpath"]

    def merge_destination(self, frontmatter, settings):
        """ Merge destination """
        if "destination" in frontmatter:
            value = frontmatter['destination']
            file_name = util.resolve_meta_path(
                path.dirname(unicode_string(value)),
                self.base
            )
            if file_name is not None and path.isdir(file_name):
                value = path.normpath(
                    path.join(file_name, path.basename(value))
                )
                if path.exists(value) and path.isdir(value):
                    value = None
            else:
                value = None
            if value is not None:
                settings["page"]["destination"] = value
            del frontmatter['destination']

    def merge_includes(self, frontmatter, settings):
        """
        Find css and js includes and merge them.
        """
        css = []
        js = []

        if "include" in frontmatter:
            value = frontmatter['include']
            if not isinstance(value, list):
                value = []
            settings["page"]['include'] = [
                unicode_string(v) for v in value if isinstance(v, string_type)
            ]
            del frontmatter['include']

        # Javascript and CSS include
        for i in ("css", "js"):
            key = 'include.%s' % i
            if key in frontmatter:
                value = frontmatter[key]
                items = []
                for j in value:
                    pth = unicode_string(j)
                    items.append(pth)
                if i == 'css':
                    css += items
                else:
                    js += items
                del frontmatter[key]

        # Append CSS and JS from built-in keys if any
        if len(css):
            settings['settings']['css'] = settings['settings'].get('css', []) + css
        if len(js):
            settings['settings']['js'] = settings['settings'].get('js', []) + js

    def merge_references(self, frontmatter, settings):
        """ Merge references """
        if 'references' in frontmatter:
            value = frontmatter['references']
            if not isinstance(value, list):
                value = [value]
            refs = []
            for v in value:
                pth = unicode_string(v)
                refs.append(pth)
            settings["page"]['references'] = refs
            del frontmatter['references']

    def merge_settings(self, frontmatter, settings):
        """ Handle and merge PyMdown settings. """
        if 'settings' in frontmatter and isinstance(frontmatter['settings'], dict):
            value = frontmatter['settings']
            for subkey, subvalue in value.items():
                # Html template
                if subkey == "template":
                    org_pth = unicode_string(subvalue)
                    new_pth = self.process_settings_path(org_pth, self.base)
                    settings['settings'][subkey] = new_pth if new_pth is not None else org_pth

                # Handle optional extention assets
                elif subkey.startswith('@'):
                    for assetkey, assetvalue in subvalue.items():
                        if assetkey in ('cs', 'js'):
                            items = []
                            for i in assetvalue:
                                pth = unicode_string(i)
                                items.append(pth)
                            settings['settings'][subkey][assetkey] = items
                        else:
                            settings['settings'][subkey][assetkey] = assetvalue

                # Javascript and CSS files
                elif subkey in ("css", "js"):
                    items = []
                    for i in subvalue:
                        pth = unicode_string(i)
                        items.append(pth)
                    settings['settings'][subkey] = items

                # All other settings that require no other special handling
                else:
                    settings['settings'][subkey] = subvalue
            del frontmatter['settings']

    def merge_meta(self, frontmatter, settings):
        """ Resolve all other frontmatter items as meta items. """
        for key, value in frontmatter.items():
            if isinstance(value, list):
                value = [unicode_string(v) for v in value]
            else:
                value = unicode_string(value)
            settings["page"]["meta"][unicode_string(key)] = value

    def merge(self, frontmatter, settings):
        """ Handle basepath first and then merge all keys. """
        self.merge_basepath(frontmatter, settings)
        self.merge_relative_path(frontmatter, settings)
        self.merge_destination(frontmatter, settings)
        self.merge_references(frontmatter, settings)
        self.merge_settings(frontmatter, settings)
        self.merge_includes(frontmatter, settings)
        self.merge_meta(frontmatter, settings)


class Settings(object):
    def __init__(self, **kwargs):
        """ Initialize """
        self.settings = {
            "page": {
                "destination": None,
                "basepath": None,
                "relpath": None,
                "references": [],
                "include": [],
                "meta": {}
            },
            "settings": {}
        }
        self.critic = kwargs.get('critic', util.CRITIC_IGNORE)
        self.plain = kwargs.get('plain', False)
        self.batch = kwargs.get('batch', False)
        self.encoding = kwargs.get('encoding', 'utf-8')
        self.output_encoding = kwargs.get('output_encoding', 'utf-8')
        self.preview = kwargs.get('preview', False)
        self.is_stream = kwargs.get('stream', False)
        self.force_stdout = kwargs.get('force_stdout', False)
        self.clean = kwargs.get('clean', False)
        self.force_no_template = kwargs.get('force_no_template', False)
        self.pygments_noclasses = False

        # Use default settings file if one was not provided
        settings_path = kwargs.get('settings_path', None)
        self.settings_path = settings_path if settings_path is not None else 'pymdown.cfg'

    def unpack_settings_file(self):
        """ Unpack default settings file. """
        text = util.load_text_resource(util.DEFAULT_SETTINGS, internal=True)
        try:
            with codecs.open(self.settings_path, "w", encoding="utf-8") as f:
                f.write(text)
        except:
            logger.Log.error(traceback.format_exc())

    def read_settings(self):
        """
        Get the settings and add absolutepath
        extention if a preview is planned.
        Unpack the settings file if needed.
        """

        settings = None

        # Unpack settings file if needed
        if not path.exists(self.settings_path):
            self.unpack_settings_file()

        # Try and read settings file
        try:
            with codecs.open(self.settings_path, "r", encoding='utf-8') as f:
                contents = f.read()
                try:
                    settings = json.loads(fstrip.json.sanitize_json(contents))
                except:
                    settings = util.yaml_load(contents)
        except:
            logger.Log.error(traceback.format_exc())

        self.settings["settings"] = settings if settings is not None else {}

    def get(self, file_name, output=None, basepath=None, relpath=None, frontmatter=None):
        """ Get the complete settings object for the given file """
        self.file_name = file_name
        settings = deepcopy(self.settings)
        settings["page"]["destination"] = util.resolve_destination(
            output,
            self.file_name,
            critic_mode=self.critic,
            batch=self.batch
        )
        settings["page"]["basepath"] = util.resolve_base_path(
            basepath,
            self.file_name,
            is_stream=self.is_stream
        )
        settings["page"]["relpath"] = util.resolve_relative_path(relpath)
        if frontmatter is not None:
            # Apply frontmatter by merging it to the settings
            merge = MergeSettings(self.file_name, self.is_stream)
            merge.merge(frontmatter, settings)

        # Store destination as our output reference directory.
        # This is used for things like converting relative paths.
        # If there is no output location, try to come up with a rational
        # output reference directory by falling back to the source file.
        if settings['page']['destination'] is not None:
            self.out = path.dirname(path.abspath(settings['page']['destination']))
        elif file_name:
            self.out = path.dirname(path.abspath(self.file_name))
        else:
            self.out = None

        # Try to come up with a sane relative path since one was not provided
        if settings['page']['relpath'] is None:
            if settings['page']['destination'] is not None:
                settings['page']['relpath'] = path.dirname(
                    path.abspath(settings['page']['destination'])
                )
            elif file_name:
                settings['page']['relpath'] = path.dirname(
                    path.abspath(self.file_name)
                )

        # Process special output flags
        if self.force_stdout:
            settings["page"]["destination"] = None
        if self.force_no_template:
            settings['settings']['template'] = None

        # Do some post processing on the settings
        self.post_process_settings(settings)
        return settings

    def set_style(self, extensions, settings):
        """
        Search the extensions for the style to be used and return it.
        If it is not explicitly set, go ahead and insert the default
        style (github).
        """
        style = None

        if not PYGMENTS_AVAILABLE:
            settings["settings"]["use_pygments_css"] = False

        # Search for codehilite to see what style is being set.
        if "markdown.extensions.codehilite" in extensions:
            config = extensions["markdown.extensions.codehilite"]
            if config is None:
                config = {}

            if not PYGMENTS_AVAILABLE and bool(config.get('use_pygments', True)):
                config['use_pygments'] = False

            if bool(config.get('noclasses', False)) or not bool(config.get('use_pygments', True)):
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
                    logger.Log.error("Cannot find style: %s! Falling back to 'default' style." % style)
                    style = "default"
            config['pygments_style'] = style

        settings["settings"]["style"] = style

    def post_process_settings(self, settings):
        """ Process the settings files making needed adjustements """

        extensions = settings["settings"].get("extensions", OrderedDict())

        # Remove critic extension if manually defined
        # and remove plainhtml if defined and --plain-html is specified on CLI
        if "pymdownx.critic" in extensions:
            del extensions["pymdownx.critic"]
        if "pymdownx.plainhtml" in extensions and self.plain:
            del extensions["pymdownx.plainhtml"]

        # Ensure previews are using absolute paths or relative paths
        if self.preview or not settings["settings"].get("disable_path_conversion", False):
            # Add pathconverter extension if not already set.
            if "pymdownx.pathconverter" not in extensions:
                extensions["pymdownx.pathconverter"] = {
                    "base_path": "${BASE_PATH}",
                    "relative_path": "${REL_PATH}" if not self.preview else "${OUTPUT}",
                    "absolute": settings["settings"].get("path_conversion_absolute", False)
                }
            elif self.preview and "pymdownx.pathconverter" in extensions:
                if extensions["pymdownx.pathconverter"] is None:
                    extensions["pymdownx.pathconverter"] = {}
                extensions["pymdownx.pathconverter"]["relative_path"] = "${OUTPUT}"

        # Add critic to the end since it is most reliable when applied to the end.
        critic_mode = "ignore"
        if self.critic & util.CRITIC_ACCEPT:
            critic_mode = "accept"
        elif self.critic & util.CRITIC_REJECT:
            critic_mode = "reject"
        elif self.critic & util.CRITIC_VIEW:
            critic_mode = "view"
        if critic_mode != "ignore":
            extensions["pymdownx.critic"] = {"mode": critic_mode}

        # Append plainhtml.
        # Most reliable when applied to the end. Okay to come after critic.
        if self.plain:
            extensions['pymdownx.plainhtml'] = None

        # Set extensions to its own key
        settings["settings"]["extensions"] = extensions

        # Set style
        self.set_style(extensions, settings)