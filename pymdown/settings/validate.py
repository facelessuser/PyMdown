"""
Validate settings.

Licensed under MIT
Copyright (c) 2014 - 2015 Isaac Muse <isaacmuse@gmail.com>
"""
from collections import OrderedDict
from .. import compat

InvalidKey = object()


def is_string(value):
    """Check if value is a unicode string."""

    return isinstance(value, compat.unicode_type)


def is_dict(value):
    """Check if value is a dict or OrderedDict."""

    return isinstance(value, (dict, OrderedDict))


def is_array(value):
    """Check if value is an array."""

    return isinstance(value, list)


def is_float(value):
    """Check if value is a float."""

    return isinstance(value, float)


def is_int(value):
    """Check if value is an int."""

    return isinstance(value, int)


def is_bool(value):
    """Check if value is a bool."""

    return isinstance(value, bool)


def is_none(value):
    """Check if value is None."""

    return value is None


def in_range(value, minimum, maximum):
    """Check if value is in range."""

    okay = True
    if minimum >= 0 and len < minimum:
        okay = False
    elif maximum >= 0 and value > maximum:
        okay = False
    return okay


class Validate(object):
    """Validate the settings object and return defaults in invalide keys if option is enabled."""

    defaults = {
        "css": [],
        "js": [],
        "use_jinja2": False,
        "jinja2_block": ["{%", "%}"],
        "jinja2_variable": ["{{", "}}"],
        "jinja2_comment": ["{#", "#}"],
        "markdown_extensions": OrderedDict(),
        "use_pygments_css": True,
        "pygments_style": 'default',
        "pygments_class": 'codehilite',
        "template": 'default/template.html',
        "disable_path_conversion": False,
        "path_conversion_absolute": False,
        "tab_length": 4,
        "lazy_ol": True,
        "smart_emphasis": False,
        "enable_attributes": True,
        "output_format": 'xhtml1',
        "extra": OrderedDict()
    }

    def __init__(self, provide_defaults=False):
        """Initialize options."""

        self.provide_defaults = provide_defaults

    def set_default(self, settings, key):
        """Set the default key."""

        settings[key] = self.defaults[key]

    def val_str_array(self, key, settings, minimum=-1, maximum=-1):
        """Validate an array of strings."""

        remove = []
        if key not in settings:
            if self.provide_defaults:
                self.set_default(settings, key)
        elif not is_array(settings[key]) or not in_range(len(settings[key]), minimum, maximum):
            if self.provide_defaults:
                self.set_default(settings, key)
            else:
                del settings[key]
        else:
            remove = []
            index = 0
            for x in settings[key]:
                if not is_string(x):
                    remove.append(index)
                index += 1
            for r in remove:
                del settings[key][r]

    def val_bool(self, key, settings):
        """Validate a bool."""

        if key not in settings:
            if self.provide_defaults:
                self.set_default(settings, key)
        elif not is_bool(settings[key]):
            if self.provide_defaults:
                self.set_default(settings, key)
            else:
                del settings[key]

    def val_int(self, key, settings):
        """Validate an int."""

        if key not in settings:
            if self.provide_defaults:
                self.set_default(settings, key)
        elif not is_int(settings[key]):
            if self.provide_defaults:
                self.set_default(settings, key)
            else:
                del settings[key]

    def val_str(self, key, settings):
        """Validate a string."""

        if key not in settings:
            if self.provide_defaults:
                self.set_default(settings, key)
        elif not is_string(settings[key]):
            if self.provide_defaults:
                self.set_default(settings, key)
            else:
                del settings[key]

    def val_extra(self, settings):
        """Validate the extra object."""

        key = 'extra'

        if key not in settings:
            if self.provide_defaults:
                self.set_default(settings, key)
        elif not is_dict(settings[key]):
            if self.provide_defaults:
                self.set_default(settings, key)
            else:
                del settings[key]

    def val_md_extensions(self, settings):
        """Ensure markdown extensions look valid."""

        key = 'markdown_extensions'

        if key not in settings:
            if self.provide_defaults:
                self.set_default(settings, key)
        elif not is_dict(settings[key]):
            if self.provide_defaults:
                self.set_default(settings, key)
            else:
                del settings[key]
        else:
            remove = []
            for k, v in settings['markdown_extensions'].items():
                if not is_string(k) or (not is_dict(v) and not is_none(v)):
                    remove.append(k)
            for r in remove:
                del settings['markdown_extensions'][r]

    def validate(self, settings):
        """Ensure the settings object is valid."""

        # Template settings
        self.val_str('template', settings)
        self.val_str_array('css', settings)
        self.val_str_array('js', settings)
        self.val_extra(settings)

        # PyMdown path conversion settings
        self.val_bool('disable_path_conversion', settings)
        self.val_bool('path_conversion_absolute', settings)

        # Pygments settings
        self.val_bool('use_pygments_css', settings)
        self.val_str('pygments_class', settings)
        self.val_str('pygments_style', settings)

        # Jinja2 settings
        self.val_bool('use_jinja2', settings)
        self.val_str_array('jinja2_block', settings, minimum=2, maximum=2)
        self.val_str_array('jinja2_variable', settings, minimum=2, maximum=2)
        self.val_str_array('jinja2_comment', settings, minimum=2, maximum=2)

        # Python Markdown settings
        self.val_int('tab_length', settings)
        self.val_bool('lazy_ol', settings)
        self.val_bool('smart_emphasis', settings)
        self.val_bool('enable_attributes', settings)
        self.val_str('output_format', settings)
        self.val_md_extensions(settings)
