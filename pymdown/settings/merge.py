"""
Merge settings.

Licensed under MIT
Copyright (c) 2014 - 2015 Isaac Muse <isaacmuse@gmail.com>
"""
from os import path
from .. import util
from .. import compat
from collections import OrderedDict
from . import validate


class MergeSettings(object):
    """
    Apply front matter to settings object etc.

    PAGE_KEYS: destination, basepath, relpath,
               js, css, title, encoding, content
    SETTINGS KEY: settings.
    EXTRA KEYS: all other keys that aren't handled above.
    """

    def __init__(self, file_name, is_stream):
        """Initialize."""

        self.file_name = file_name
        self.is_stream = is_stream
        self.base = None
        self.css = []
        self.js = []

    def process_settings_path(self, pth, base):
        """General method to process paths in settings file."""

        encoding = util.splitenc(pth)[1]

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
        """Merge the basepath."""

        if "basepath" in frontmatter:
            value = frontmatter["basepath"]
            if validate.is_string(value):
                settings["page"]["basepath"] = util.resolve_base_path(
                    value,
                    self.file_name,
                    is_stream=self.is_stream
                )
            del frontmatter["basepath"]
        self.base = settings["page"]["basepath"]

    def merge_relative_path(self, frontmatter, settings):
        """Merge the relative path."""

        if "relpath" in frontmatter:
            value = frontmatter["relpath"]
            if validate.is_string(value):
                settings["page"]["relpath"] = util.resolve_relative_path(value)
            del self.frontmatter["relpath"]

    def merge_destination(self, frontmatter, settings):
        """Merge destination."""

        if "destination" in frontmatter:
            value = frontmatter['destination']
            if validate.is_string(value):
                file_name = util.resolve_meta_path(
                    path.dirname(value),
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
        """Find css and js includes and merge them."""

        css = settings['settings'].get('css', [])
        js = settings['settings'].get('js', [])

        # Javascript and CSS include
        for key in ("css", "js"):
            if key in frontmatter:
                value = frontmatter[key]
                if validate.is_array(value):
                    locals()[key] += [v for v in value if validate.is_string(v)]
                del frontmatter[key]

        settings['page']['css'] += css
        settings['page']['js'] += js

    def merge_settings(self, frontmatter, settings):
        """Handle and merge PyMdown settings."""

        value = frontmatter['settings']
        for subkey, subvalue in value.items():

            # Html template
            if subkey == "template" and isinstance(subvalue, compat.unicode_type):
                org_pth = subvalue
                new_pth = self.process_settings_path(org_pth, self.base)
                settings['settings'][subkey] = new_pth if new_pth is not None else org_pth

            # All other settings that require no other special handling
            else:
                settings['settings'][subkey] = subvalue
        del frontmatter['settings']

    def merge_meta(self, frontmatter, settings):
        """Resolve all other frontmatter items as meta/extra items."""

        settings["extra"] = settings["settings"].get("extra", OrderedDict())

        for key, value in frontmatter.items():
            if key == 'title' and validate.is_string(value):
                settings["page"]["title"] = value

            settings["extra"][key] = value

    def merge(self, frontmatter, settings):
        """Handle basepath first and then merge all keys."""

        if 'settings' in frontmatter and validate.is_dict(frontmatter['settings']):
            validate.Validate().validate(frontmatter['settings'])
        else:
            frontmatter['settings'] = OrderedDict()
        self.merge_basepath(frontmatter, settings)
        self.merge_relative_path(frontmatter, settings)
        self.merge_destination(frontmatter, settings)
        self.merge_settings(frontmatter, settings)
        self.merge_includes(frontmatter, settings)
        self.merge_meta(frontmatter, settings)
