"""
PyMdown Settings.

Manage Settings

Licensed under MIT
Copyright (c) 2014 - 2015 Isaac Muse <isaacmuse@gmail.com>
"""
from __future__ import unicode_literals
from __future__ import absolute_import
import codecs
import traceback
import os.path as path
import cgi
from collections import OrderedDict
from copy import deepcopy
from . import util
from . import logger
from . import compat
try:
    from pygments.styles import get_style_by_name, get_formatter_by_name
    PYGMENTS_AVAILABLE = True
except Exception:  # pragma: no cover
    PYGMENTS_AVAILABLE = False


def get_pygment_style(style, css_class='codehilite'):
    """Get the specified pygments sytle CSS."""

    try:
        # Try and request pygments to generate it
        text = get_formatter_by_name('html', style=style).get_style_defs('.' + css_class)
    except Exception:
        # Try and request pygments to generate default
        text = get_formatter_by_name('html', style="default").get_style_defs('.' + css_class)
    return '<style>\n%s\n</style>\n' % text if text is not None else ""


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

    def merge_settings(self, frontmatter, settings):
        """Handle and merge PyMdown settings."""

        if 'use_template' in frontmatter:
            if isinstance(frontmatter['use_template'], bool):
                settings['settings']['use_template'] = frontmatter['use_template']
            del frontmatter['use_template']

        if 'settings' in frontmatter and isinstance(frontmatter['settings'], (dict, OrderedDict)):
            value = frontmatter['settings']
            for subkey, subvalue in value.items():
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
        self.merge_settings(frontmatter, settings)
        self.merge_includes(frontmatter, settings)
        self.merge_meta(frontmatter, settings)


class Settings(object):

    """
    Settings object for merging global settings with frontmatter.

    Contains global settings, and a user can
    retrieve a settings dict merged with a file's frontmatter.
    """

    def __init__(self, **kwargs):
        """Initialize."""

        self.settings = {
            "page": {
                "title": None,
                "encoding": kwargs.get('output_encoding', 'utf-8'),
                "destination": None,
                "basepath": None,
                "relpath": None,
                "css": [],
                "js": [],
                "content": '',
            },
            "extra": {},
            "settings": {}
        }
        self.critic = kwargs.get('critic', util.CRITIC_IGNORE)
        self.plain = kwargs.get('plain', False)
        self.batch = kwargs.get('batch', False)
        self.encoding = kwargs.get('encoding', 'utf-8')
        self.preview = kwargs.get('preview', False)
        self.is_stream = kwargs.get('stream', False)
        self.force_stdout = kwargs.get('force_stdout', False)
        self.force_no_template = kwargs.get('force_no_template', False)
        self.pygments_noclasses = False

        # Use default settings file if one was not provided
        settings_path = kwargs.get('settings_path', None)
        self.settings_path = settings_path if settings_path is not None else path.basename(util.DEFAULT_SETTINGS)

    def unpack_settings_file(self):  # pragma: no cover
        """Unpack default settings file."""

        text = util.load_text_resource(util.DEFAULT_SETTINGS, internal=True)
        try:
            with codecs.open(self.settings_path, "w", encoding="utf-8") as f:
                f.write(text)
        except Exception:
            logger.Log.error(traceback.format_exc())

    def read_settings(self):
        """
        Get and read the settings.

        Unpack the settings file if needed.
        """

        settings = None

        # Unpack settings file if needed
        if not path.exists(self.settings_path):
            self.unpack_settings_file()  # pragma: no cover

        # Try and read settings file
        try:
            with codecs.open(self.settings_path, "r", encoding='utf-8') as f:
                contents = f.read()
                settings = util.yaml_load(contents)
        except Exception:  # pragma: no cover
            logger.Log.error(traceback.format_exc())

        self.settings["settings"] = settings if settings is not None else {}

    def get(self, file_name, **kwargs):
        """Get the complete settings object for the given file."""

        output = kwargs.get('output', None)
        basepath = kwargs.get('basepath', None)
        relpath = kwargs.get('relpath', None)
        frontmatter = kwargs.get('frontmatter', None)
        title = kwargs.get('title', None)

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

        # Handle title
        if title is None and file_name is not None:
            title = path.splitext(path.basename(path.abspath(file_name)))[0]
        if settings["page"]["title"] is not None:
            title = settings["page"]["title"]
        else:
            title = compat.to_unicode(title) if title else "Untitled"
        settings["page"]["title"] = cgi.escape(title)

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

    def load_highlight(self, highlight_style, use_pygments_css, pygments_class):
        """Load Syntax highlighter CSS."""

        style = None

        if not self.plain:
            if PYGMENTS_AVAILABLE and highlight_style is not None and use_pygments_css:
                # Ensure pygments is enabled in the highlighter
                style = get_pygment_style(highlight_style, pygments_class)

        return style

    def set_style(self, extensions, settings):
        """
        Search the extensions for the style to be used and return it.

        If it is not explicitly set, go ahead and insert the default
        style (github).
        """
        style = 'default'

        if not PYGMENTS_AVAILABLE:  # pragma: no cover
            settings["settings"]["use_pygments_css"] = False

        global_use_pygments_css = settings["settings"].get("use_pygments_css", True)
        use_pygments_css = False
        for hilite_ext in ('markdown.extensions.codehilite', 'pymdownx.inlinehilite'):
            if hilite_ext not in extensions:
                continue
            # Search for codehilite to see what style is being set.
            config = extensions[hilite_ext]
            if config is None:
                config = {}

            use_pygments_css = use_pygments_css or (
                not config.get('noclasses', False) and
                config.get('use_pygments', True) and
                config.get('use_codehilite_settings', True) and
                PYGMENTS_AVAILABLE and
                global_use_pygments_css
            )

        if global_use_pygments_css and not use_pygments_css:
            settings["settings"]["use_pygments_css"] = False

        if use_pygments_css:
            # Ensure a working style is set
            style = settings["settings"].get('pygments_style', None)
            if style is None:
                # Explicitly define a pygment style and store the name
                # This is to ensure the "noclasses" option always works
                style = "default"
            else:
                try:
                    # Check if the desired style exists internally
                    get_style_by_name(style)
                except Exception:
                    logger.Log.error("Cannot find style: %s! Falling back to 'default' style." % style)
                    style = "default"

        settings["settings"]["pygments_style"] = style

        settings["page"]["pygments_style"] = self.load_highlight(
            style,
            settings["settings"]["use_pygments_css"],
            settings["settings"].get('pygments_class', 'codehilite')
        )

    def post_process_settings(self, settings):
        """Process the settings files making needed adjustement."""

        extensions = settings["settings"].get("markdown_extensions", OrderedDict())

        critic_mode = "ignore"
        if self.critic & util.CRITIC_ACCEPT:
            critic_mode = "accept"
        elif self.critic & util.CRITIC_REJECT:
            critic_mode = "reject"
        elif self.critic & util.CRITIC_VIEW:
            critic_mode = "view"

        # Remove critic extension if manually defined
        # and remove plainhtml if defined and --plain-html is specified on CLI
        if "pymdownx.critic" in extensions and critic_mode != 'ignore':
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
        if critic_mode != "ignore":
            extensions["pymdownx.critic"] = {"mode": critic_mode}

        # Append plainhtml.
        # Most reliable when applied to the end. Okay to come after critic.
        if self.plain:
            extensions['pymdownx.plainhtml'] = None

        # Set extensions to its own key
        settings["settings"]["markdown_extensions"] = extensions

        # Set style
        self.set_style(extensions, settings)
