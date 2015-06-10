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
import os
from . import logger
from . import compat
from .template import Template


class PyMdownFormatterException(Exception):

    """PyMdown formatter exception."""


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
        self.preview = kwargs.get("preview", False)
        self.encoding = settings.get("page", {}).get("encoding", "utf-8")
        self.basepath = settings.get("page", {}).get("basepath", None)
        self.relpath = settings.get("page", {}).get("relpath", None)
        self.output = settings.get("page", {}).get("destination", None)
        self.template_file = self.settings.get("template", None) if not settings.get("plain", False) else None
        self.encode_file = True
        self.file = None

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
                self.relpath = os.path.dirname(self.file.name)
        except Exception:
            logger.Log.error(str(traceback.format_exc()))
            raise PyMdownFormatterException("Could not open output file!")

    def close(self):
        """Close the output file."""

        if self.file:
            self.file.close()

    def write(self, text):
        """Write the given text to the output file."""

        self.page["content"] = text

        template = Template(
            basepath=self.basepath,
            relpath=self.relpath,
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
