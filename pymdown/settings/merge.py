"""
Merge settings.

Licensed under MIT
Copyright (c) 2014 - 2015 Isaac Muse <isaacmuse@gmail.com>
"""
from os import path
from .. import util
from .. import compat
from collections import OrderedDict


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
            if isinstance(value, compat.unicode_type):
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
            if isinstance(value, compat.unicode_type):
                settings["page"]["relpath"] = util.resolve_relative_path(value)
            del self.frontmatter["relpath"]

    def merge_destination(self, frontmatter, settings):
        """Merge destinatio."""

        if "destination" in frontmatter:
            value = frontmatter['destination']
            if isinstance(value, compat.unicode_type):
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
                if isinstance(value, list):
                    locals()[key] += [v for v in value if isinstance(v, compat.unicode_type)]
                del frontmatter[key]

        settings['page']['css'] += css
        settings['page']['js'] += js

    def merge_template_settings(self, frontmatter, settings):
        """Merge special template variables."""

        if 'use_template' in frontmatter:
            if isinstance(frontmatter['use_template'], bool):
                settings['settings']['use_template'] = frontmatter['use_template']
            del frontmatter['use_template']
        if 'template_tags' in frontmatter:
            if isinstance(frontmatter['template_tags'], (dict, OrderedDict)):
                for key, value in frontmatter['template_tags'].items():
                    if key in ('block', 'variable', 'comment') and len(value) == 2:
                        if isinstance(value[0], compat.unicode_type) and isinstance(value[1], compat.unicode_type):
                            settings['settings']['template_tags'][key] = value
            del frontmatter['template_tags']

    def merge_settings(self, frontmatter, settings):
        """Handle and merge PyMdown settings."""

        if 'settings' in frontmatter and isinstance(frontmatter['settings'], (dict, OrderedDict)):
            value = frontmatter['settings']
            for subkey, subvalue in value.items():
                if subkey in ('use_template', 'template_tags'):
                    # Ignore template variables as these should only be in the frontmatter
                    continue
                # Html template
                if subkey == "template" and isinstance(subvalue, compat.unicode_type):
                    org_pth = subvalue
                    new_pth = self.process_settings_path(org_pth, self.base)
                    settings['settings'][subkey] = new_pth if new_pth is not None else org_pth

                # Javascript and CSS files
                elif subkey in ("css", "js") and isinstance(subvalue, compat.unicode_type):
                    settings['settings'][subkey] = [
                        v for v in subvalue if isinstance(v, compat.unicode_type)
                    ]
                elif subkey == "extra" and isinstance(subvalue, (dict, OrderedDict)):
                    settings['settings'][subkey] = subvalue

                # All other settings that require no other special handling
                else:
                    settings['settings'][subkey] = subvalue
            del frontmatter['settings']

    def merge_meta(self, frontmatter, settings):
        """Resolve all other frontmatter items as meta/extra items."""

        if settings["settings"].get('extra') and isinstance(settings["settings"].get('extra'), (dict, OrderedDict)):
            settings["extra"] = settings["settings"].get("extra", {})

        for key, value in frontmatter.items():
            if key == 'title' and isinstance(value, compat.unicode_type):
                settings["page"]["title"] = value

            settings["extra"][key] = value

    def merge(self, frontmatter, settings):
        """Handle basepath first and then merge all keys."""

        self.merge_basepath(frontmatter, settings)
        self.merge_relative_path(frontmatter, settings)
        self.merge_destination(frontmatter, settings)
        self.merge_template_settings(frontmatter, settings)
        self.merge_settings(frontmatter, settings)
        self.merge_includes(frontmatter, settings)
        self.merge_meta(frontmatter, settings)
