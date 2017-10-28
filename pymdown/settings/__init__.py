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
from .. import util
from .. import logger
from .. import compat
from .merge import MergeSettings
from .validate import Validate
try:
    from pygments.styles import get_style_by_name
    from pygments.formatters import get_formatter_by_name
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
        self.encoding = util._get_encoding(kwargs.get('encoding', 'utf-8'))
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

        if settings is None:
            settings = OrderedDict()

        Validate(provide_defaults=True).validate(settings)

        self.settings["settings"] = settings

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
            if highlight_style is not None and use_pygments_css:
                # Ensure pygments is enabled in the highlighter
                style = get_pygment_style(highlight_style, pygments_class)

        return style

    def set_style(self, extensions, settings):
        """Load up needed Pygments style."""

        style = settings["settings"]['pygments_style']

        if not PYGMENTS_AVAILABLE:  # pragma: no cover
            settings["settings"]["use_pygments_css"] = False

        if settings["settings"]["use_pygments_css"]:
            # Ensure a working style is set
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
            settings["settings"]['pygments_class']
        )

    def post_process_settings(self, settings):
        """Process the settings files making needed adjustement."""

        extensions = settings["settings"]["markdown_extensions"]

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
        if self.preview or not settings["settings"]["disable_path_conversion"]:
            # Add pathconverter extension if not already set.
            if "pymdownx.pathconverter" not in extensions:
                extensions["pymdownx.pathconverter"] = {
                    "base_path": "${BASE_PATH}",
                    "relative_path": "${REL_PATH}" if not self.preview else "${OUTPUT}",
                    "absolute": settings["settings"]["path_conversion_absolute"]
                }
            elif self.preview and "pymdownx.pathconverter" in extensions:
                if extensions["pymdownx.pathconverter"] is None:
                    extensions["pymdownx.pathconverter"] = {}
                if "base_path" not in extensions["pymdownx.pathconverter"]:
                    extensions["pymdownx.pathconverter"]["base_path"] = "${BASE_PATH}"
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
