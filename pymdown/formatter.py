"""
Formatter.

Places markdown in HTML with the specified CSS and JS etc.

Licensed under MIT
Copyright (c) 2014 - 2015 Isaac Muse <isaacmuse@gmail.com>
"""
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function
import codecs
import traceback
import tempfile
import cgi
from copy import deepcopy
from . import util
from . import logger
from . import compat
from .template import Template
try:
    from pygments.formatters import get_formatter_by_name
    PYGMENTS_AVAILABLE = True
except Exception:  # pragma: no cover
    PYGMENTS_AVAILABLE = False


class PyMdownFormatterException(Exception):

    """PyMdown formatter exception."""

    pass


def get_pygment_style(style, css_class='codehilite'):
    """Get the specified pygments sytle CSS."""

    try:
        # Try and request pygments to generate it
        text = get_formatter_by_name('html', style=style).get_style_defs('.' + css_class)
    except Exception:
        # Try and request pygments to generate default
        text = get_formatter_by_name('html', style="default").get_style_defs('.' + css_class)
    return '<style>\n%s\n</style>\n' % text if text is not None else ""


class Terminal(object):

    """Have console output mimic the file output calls."""

    name = None

    def __init__(self, encoding="utf-8"):
        """Initialize."""

        self.encoding = encoding

    def write(self, text):
        """Dump texst to screen."""

        compat.print_stdout(text, self.encoding)

    def close(self):
        """There is nothing to close."""

        pass


class Text(object):

    """Text output object."""

    def __init__(self, settings):
        """Initialize Text object."""

        self.encode_file = True
        self.file = None
        self.encoding = settings("page", {}).get("encoding", 'utf-8')
        self.output = settings("page", {}).get("destination", None)

    def open(self):
        """
        Open output stream.

        Set the correct output target and create the file if necessary.
        """

        if self.output is None:
            self.file = Terminal(self.encoding)
        else:
            try:
                self.file = codecs.open(self.output, "w", encoding=self.encoding)
                self.encode_file = False
            except Exception:
                logger.Log.error(str(traceback.format_exc()))
                raise PyMdownFormatterException("Could not open output file!")

    def write(self, text):
        """Write the content."""

        self.file.write(
            text.encode(self.encoding, errors="xmlcharrefreplace") if self.encode_file else text
        )

    def close(self):
        """Close the file."""

        if self.file:
            self.file.close()


class Html(object):

    """HTML output object."""

    def __init__(self, **kwargs):
        """Initialize."""
        settings = kwargs["settings"]
        self.settings = settings.get("settings", {})
        self.page = settings.get("page", {})
        self.extra = settings.get("extra", {})
        self.plain = settings.get("plain", False)
        self.preview = kwargs.get("preview", False)
        self.encoding = settings.get("page", {}).get("encoding", "utf-8")
        self.basepath = settings.get("page", {}).get("basepath", None)
        self.relpath = settings.get("page", {}).get("relpath", None)
        self.output = settings.get("page", {}).get("destination", None)
        self.template_file = self.settings.get("template", None) if not self.plain else None
        self.encode_file = True
        self.added_res = set()
        self.template = None
        self.file = None
        self.user_path = util.get_user_path()

    def update_template_variables(self, text, meta):
        """
        Update date template variables with meta info acquired from file and from settings.

            - page.title: Update title with meta if none was found in frontmatter.
            - page.pygments_style: Update pygments style if allowed in settings.
            - page.content:  The HTML content acquied from the markdown source.
            - extra: Update any "extra" content found in meta that isn't already defined.
        """

        title = "Untitled"
        if "title" in meta and isinstance(meta["title"], compat.string_type):
            title = compat.to_unicode(meta["title"])
            del meta["title"]
        if self.page["title"] is not None:
            title = compat.to_unicode(self.page["title"])

        self.page["title"] = cgi.escape(title)
        self.page["pygments_style"] = self.load_highlight(self.settings.get("pygments_style", None))
        self.page["content"] = text

        # Merge the meta data
        for extras in (meta, self.settings.get('extra', {})):
            for k, v in deepcopy(extras).items():
                if k not in self.extra:
                    self.extra[k] = v

    def open(self):
        """Set and create the output target and target related flags."""

        if self.output is None:
            self.file = Terminal(self.encoding)
            self.file.name = self.relpath
        try:
            if not self.preview and self.output is not None:
                self.file = codecs.open(
                    self.output, "w",
                    encoding=self.encoding,
                    errors="xmlcharrefreplace"
                )
                self.encode_file = False
            elif self.preview:
                self.file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
        except Exception:
            logger.Log.error(str(traceback.format_exc()))
            raise PyMdownFormatterException("Could not open output file!")

    def close(self):
        """Close the output file."""

        if self.file:
            self.file.close()

    def write(self, text, meta=None):
        """Write the given text to the output file."""

        if meta is None:
            meta = {}

        self.update_template_variables(text, meta)

        template = Template(
            basepath=self.basepath,
            relpath=self.relpath,
            userpath=self.user_path,
            force_conversion=self.preview,
            disable_path_conversion=self.settings.get("disable_path_conversion", False),
            absolute_path_conversion=self.settings.get("path_conversion_absolute", False)
        ).get_template(self.template_file)

        html = template.render(
            page=self.page,
            settings=self.settings,
            extra=self.extra
        )

        self.file.write(
            html.encode(self.encoding, errors="xmlcharrefreplace") if self.encode_file else html
        )

    def load_highlight(self, highlight_style):
        """Load Syntax highlighter CSS."""

        style = None

        if not self.plain:
            use_pygments_css = bool(self.settings.get("use_pygments_css", True))
            if PYGMENTS_AVAILABLE and highlight_style is not None and use_pygments_css:
                # Ensure pygments is enabled in the highlighter
                style = get_pygment_style(
                    highlight_style,
                    self.settings.get("pygments_class", "codehilite")
                )

        return style
