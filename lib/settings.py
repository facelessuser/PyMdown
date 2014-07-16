#!/usr/bin/env python
"""
Mdown logger

Simple class for controlling when to log to stdout

Licensed under MIT
Copyright (c) 2014 Isaac Muse <isaacmuse@gmail.com>
"""
import json
import re
import codecs
import traceback
import sys
from copy import deepcopy
from os.path import dirname, abspath, exists, normpath, expanduser
from os.path import isfile, isdir, splitext, join, basename
from . import critic_dump as cd
from . import resources as res
from .logger import Logger
from .file_strip.json import sanitize_json


BUILTIN_KEYS = ('destination', 'basepath', 'references')


class MdownSettingsException(Exception):
    pass


def is_abs(pth):
    absolute = False
    if pth is not None:
        if sys.platform.startswith('win'):
            re_win_drive = re.compile(r"(^[A-Za-z]{1}:(?:\\|/))")
            if re_win_drive.match(pth) is not None or pth.startswith("//"):
                absolute = True
        elif pth.startswith('/'):
            absolute = True
    return absolute


class Settings(object):
    def __init__(
        self, settings_path=None, stream=False,
        batch=False, critic=cd.CRITIC_IGNORE,
        plain=False, preview=False, encoding='utf-8'
    ):
        """ Initialize """
        self.critic = critic
        self.plain = plain
        self.batch = batch
        self.encoding = encoding
        self.preview = preview
        self.is_stream = stream
        self.pygments_noclasses = False
        self.settings = {
            "builtin": {
                "destination": None,
                "basepath": None,
                "references": []
            },
            "settings": {},
            "meta": {}
        }

        # Use default file if one was not provided
        if settings_path is None or not exists(settings_path):
            settings_path = join(res.RESOURCE_PATH, "mdown.json")

        # Get the settings if available
        self.read_settings(settings_path)

    def read_settings(self, settings_path):
        """
        Get the settings and add absolutepath
        extention if a preview is planned.
        Unpack the settings file if needed.
        """

        # Unpack default settings file if needed
        if not exists(settings_path):
            text = res.load_text_resource("mdown.json")
            try:
                with codecs.open(settings_path, "w", encoding="utf-8") as f:
                    f.write(text)
            except:
                Logger.log(traceback.format_exc())

        # Try and read settings file
        settings = {}
        try:
            with open(settings_path, "r") as f:
                settings = json.loads(sanitize_json(f.read()))
        except:
            Logger.log(traceback.format_exc())
            raise MdownSettingsException("Could not parse settings file!")

        self.settings["settings"] = settings

    def get(self, file_name, output, basepath, frontmatter=None):
        """ Get the complete settings object for the given file """
        self.file_name = file_name
        settings = deepcopy(self.settings)
        settings["builtin"]["destination"] = self.get_output(output)
        settings["builtin"]["basepath"] = self.get_base_path(basepath)
        if frontmatter is not None:
            self.apply_frontmatter(frontmatter, settings)
        self.post_process_settings(settings)
        return settings

    def resolve_meta_path(self, target, basepath):
        """
        Resolve the path returned in the meta data.
        1. See if path is defined as absolute and if so see
           if it exists
        2. If relative, use the file's current directory
           (if available) as the base and see if the file
           can be found
        3. If relative, and the file's current directory
           as the base proved fruitless, use the defined
           basepath (if available)
        """
        current_dir = None if self.file_name is None else dirname(self.file_name)
        if target is not None:
            target = expanduser(target)
            if not is_abs(target):
                for base in (current_dir, basepath):
                    if base is not None:
                        temp = join(base, target)
                        if exists(temp):
                            target = temp
                            break
            elif not exists(target):
                target = None
        return target

    def apply_frontmatter(self, frontmatter, settings):
        """ Apply front matter to settings object etc. """

        # Handle basepath first
        if "basepath" in frontmatter:
            value = frontmatter["basepath"]
            settings["builtin"]["basepath"] = self.get_base_path(value)
            del frontmatter["basepath"]

        for key, value in frontmatter.items():
            if key == "settings" and isinstance(value, dict):
                for subkey, subvalue in value.items():
                    settings[key][subkey] = subvalue
            elif key in BUILTIN_KEYS:
                if key == "destination":
                    file_name = self.resolve_meta_path(dirname(value), settings["builtin"]["basepath"])
                    if file_name is not None and isdir(file_name):
                        value = normpath(join(file_name, basename(value)))
                        if exists(value) and isdir(value):
                            value = None
                    else:
                        value = None
                    settings["builtin"][key] = value
                elif key == "references":
                    if not isinstance(value, list):
                        value = [value]
                    refs = []
                    for v in value:
                        file_name = self.resolve_meta_path(v, settings["builtin"]["basepath"])
                        if file_name is not None and not isdir(file_name):
                            refs.append(normpath(file_name))
                    settings["builtin"][key] = refs
            else:
                if isinstance(value, list):
                    value = [str(v) for v in value]
                else:
                    value = str(value)
                settings["meta"][str(key)] = value

    def get_output(self, out_name):
        """ Get the path to output the file. """

        critic_enabled = self.critic & cd.CRITIC_ACCEPT or self.critic & cd.CRITIC_REJECT
        output = None
        if out_name is not None:
            out_name = expanduser(out_name)
        if not self.batch:
            if out_name is not None:
                name = abspath(out_name)
                if isdir(out_name):
                    Logger.log("'%s' is a directory!" % name)
                elif exists(dirname(name)):
                    output = name
                else:
                    Logger.log("'%s' directory does not exist!" % name)
        else:
            name = abspath(self.file_name)
            if self.critic & cd.CRITIC_DUMP and critic_enabled:
                if self.critic & cd.CRITIC_REJECT:
                    label = ".rejected"
                else:
                    label = ".accepted"
                base, ext = splitext(abspath(self.file_name))
                output = join(name, "%s%s%s" % (base, label, ext))
            else:
                output = join(name, "%s.html" % splitext(abspath(self.file_name))[0])

        return output

    def get_base_path(self, basepath):
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

    def set_style(self, extensions):
        """
        Search the extensions for the style to be used and return it.
        If it is not explicitly set, go ahead and insert the default
        style (github).
        """
        style = None
        re_pygment = r"pygments_style\s*=\s*([a-zA-Z][a-zA-Z_\d]*)"
        re_insert_pygment = re.compile(r"(?P<bracket_start>codehilite\([^)]+?)(?P<bracket_end>\s*\)$)|(?P<start>codehilite)")
        re_no_classes = re.compile(r"noclasses\s*=\s*(True|False)")
        self.pygments_noclasses = False
        count = 0
        for e in extensions:
            # Search for codhilite to see what style is being set.
            if e.startswith("codehilite"):
                pygments_style = re.search(re_pygment, e)
                if pygments_style is None:
                    # Explicitly define a pygment style and store the name
                    # This is to ensure the "noclasses" option always works
                    style = "github"
                    m = re_insert_pygment.match(e)
                    if m is not None:
                        if m.group('bracket_start'):
                            start = m.group('bracket_start') + ',pygments_style='
                            end = ")"
                        else:
                            start = m.group('start') + "(pygments_style="
                            end = ')'
                        extensions[count] = start + style + end
                else:
                    # Store pygment style name
                    style = "github" if pygments_style is None else pygments_style.group(1)

                # Track if the "noclasses" settings option is enabled
                noclasses = re_no_classes.search(e)
                if noclasses is not None and noclasses.group(1) == "True":
                    self.pygments_noclasses = True
            count += 1
        return style

    def post_process_settings(self, settings):
        """ Process the settings files making needed adjustements """

        absolute = False
        critic_found = []
        plain_html = []

        # Copy extensions; we will move it to its own key later
        if "extensions" in settings["settings"]:
            extensions = deepcopy(settings["settings"].get("extensions", []))
            del settings["settings"]["extensions"]

        # Log whether:
        #    - absolute paths is enabled,
        #    - Where the critic extension is enabled
        #    - Where the plainhtml plugin is enabled
        for i in range(0, len(extensions)):
            name = extensions[i]
            if name.startswith("mdownx.absolutepath"):
                absolute = True
            if name.startswith("mdownx.critic"):
                critic_found.append(i)
            if name.startswith("mdownx.plainhtml"):
                plain_html.append(i)

        indexes = list(set(critic_found + plain_html))
        indexes.sort()
        # Ensure the user can never set critic and plain text mode directly
        for index in reversed(indexes):
            del extensions[index]

        # Ensure previews are using absolute paths if not already
        if self.preview and not absolute:
            extensions.append("mdownx.absolutepath(base_path=${BASE_PATH})")

        # Handle the appropriate critic mode internally
        # Critic must be appended to end of extension list
        if self.critic != cd.CRITIC_OFF:
            mode = "ignore"
            if self.critic & cd.CRITIC_ACCEPT:
                mode = "accept"
            elif self.critic & cd.CRITIC_REJECT:
                mode = "reject"
            extensions.append("mdownx.critic(mode=%s)" % mode)

        # Handle plainhtml internally.
        # Must be appended to the end. Okay to come after critic.
        if self.plain:
            extensions.append("mdownx.plainhtml")

        # Set extensions to its own key
        settings["extensions"] = extensions

        # Set style
        settings["settings"]["style"] = self.set_style(extensions)
