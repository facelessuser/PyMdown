#!/usr/bin/env python
"""
Formatter

Places markdown in HTML with the specified CSS and JS etc.

Licensed under MIT
Copyright (c) 2014 Isaac Muse <isaacmuse@gmail.com>
"""
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
import codecs
import traceback
import re
import tempfile
from pygments.formatters import HtmlFormatter
from os.path import exists, isfile
from .resources import load_text_resource
from .logger import Logger
import cgi
import sys

PY3 = sys.version_info >= (3, 0)

if PY3:
    unicode_string = str
else:
    unicode_string = unicode  # flake8: noqa

RE_URL_START = r"https?://"


class PyMdownFormatterException(Exception):
    pass


def get_default_template():
    """ Return the default template """
    return load_text_resource("stylesheets", "default-template.html")


def get_default_css():
    """ Get the default CSS style """
    css = []
    css.append(load_text_resource("stylesheets", "default-markdown.css"))
    return css


def get_js(js, link=False):
    """ Get the specified JS code """
    if link:
        return '<script type="text/javascript" charset="utf-8" src="%s"></script>\n' % js
    else:
        return '<script type="text/javascript">\n%s\n</script>\n' % js if js is not None else ""


def get_style(style, link=False):
    """ Get the specified CSS code """
    if link:
        return '<link href="%s" rel="stylesheet" type="text/css">\n' % style
    else:
        return '<style>\n%s\n</style>\n' % style if style is not None else ""


def get_pygment_style(style):
    """ Get the specified pygments sytle CSS """
    try:
        # Try and request pygments to generate it
        text = HtmlFormatter(style=style).get_style_defs('.codehilite pre')
    except:
        # Try and request pygments to generate default
        text = HtmlFormatter(style="github").get_style_defs('.codehilite pre')
    return '<style>\n%s\n</style>\n' % text if text is not None else ""


class Terminal(object):
    """ Have console output mimic the file output calls """
    name = None

    def write(self, text):
        """ Dump texst to screen """
        print(text)

    def close(self):
        """ There is nothing to close """
        pass


class Html(object):
    def __init__(
        self, output, preview=False, title=None,
        plain=False, noclasses=False, settings={}
    ):
        self.settings = settings
        self.encode_file = True
        self.body_end = None
        self.plain = plain
        self.template = ''
        self.noclasses = noclasses
        self.title = "Untitled"
        self.set_output(output, preview)
        self.load_header(
            self.settings.get("style", None)
        )
        self.started = False

    def set_meta(self, meta):
        """ Create meta data tags """
        if "title" in meta:
            value = meta["title"]
            if isinstance(value, list):
                if len(value) == 0:
                    value = ""
                else:
                    value = value[0]
            self.title = unicode_string(value)
            del meta["title"]

        for k, v in meta.items():
            if isinstance(v, list):
                v = ','.join(v)
            if v is not None:
                self.meta.append(
                    '<meta name="%s" content="%s">' % (
                        cgi.escape(unicode_string(k), True),
                        cgi.escape(unicode_string(v), True)
                    )
                )

    def write_html_start(self):
        """ Output the HTML head and body up to the {{ BODY }} specifier """
        template = self.settings.get("html_template", "default")
        if template == "default" or not exists(template):
            template = get_default_template()
        else:
            try:
                with codecs.open(template, "r", encoding="utf-8") as f:
                    template = f.read()
            except:
                Logger.log(str(traceback.format_exc()))
                template = get_default_template()
        self.template = template

        if self.template != "":
            m = re.search(r"\{\{ BODY \}\}", template)
            if m:
                meta = '\n'.join(self.meta) + '\n'
                title = '<title>%s</title>\n' % cgi.escape(self.title)
                self.write(
                    template[0:m.start(0)].replace(
                        "{{ HEAD }}", meta + self.head + title, 1
                    )
                )
                self.body_end = m.end(0)

    def set_output(self, output, preview):
        """ Set and create the output target and target related flags """
        if output is None:
            self.file = Terminal()
        try:
            if not preview and output is not None:
                self.file = codecs.open(output, "w", encoding="utf-8", errors="xmlcharrefreplace")
                self.encode_file = False
            elif preview:
                self.file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
        except:
            Logger.log(str(traceback.format_exc()))
            raise PyMdownFormatterException("Could not open output file!")

    def close(self):
        """ Close the output file """
        if self.body_end is not None:
            self.write(self.template[self.body_end:])
        self.file.close()

    def write(self, text):
        """ Write the given text to the output file """
        if not self.plain and not self.started:
            # If we haven't already, print the file head
            self.started = True
            self.write_html_start()
        self.file.write(
            text.encode("utf-8", errors="xmlcharrefreplace") if self.encode_file else text
        )

    def load_highlight(self, highlight_style):
        """ Load Syntax highlighter CSS """
        style = None
        if highlight_style is not None and not self.noclasses:
            # Ensure pygments is enabled in the highlighter
            style = get_pygment_style(highlight_style)

        css = []
        if style is not None:
            css.append(style)

        return css

    def load_css(self, style):
        """ Load specified CSS sources """
        user_css = self.settings.get("css_style_sheets", "default")
        css = []
        if isinstance(user_css, list) and len(user_css):
            for pth in user_css:
                c = unicode_string(pth)
                if c == "default":
                    for c in get_default_css():
                        css.append(get_style(c))
                if re.match(RE_URL_START, c) is not None:
                    css.append(get_style(c, link=True))
                elif exists(c) and isfile(c):
                    try:
                        with codecs.open(c, "r", "utf-8") as f:
                            css.append(get_style(f.read()))
                    except:
                        Logger.log(str(traceback.format_exc()))

        css += self.load_highlight(style)
        return ''.join(css)

    def load_js(self):
        """ Load specified JS sources """
        user_js = self.settings.get("js_scripts", [])
        scripts = []
        if isinstance(user_js, list) and len(user_js):
            for pth in user_js:
                js = unicode_string(pth)
                if exists(js):
                    try:
                        with codecs.open(js, "r", encoding="utf-8") as f:
                            scripts.append(
                                get_js(f.read())
                            )
                    except:
                        Logger.log(str(traceback.format_exc()))
                else:
                    scripts.append(get_js(js, link=True))
        return ''.join(scripts)

    def load_header(self, style):
        """ Load up header related info """
        self.meta = ['<meta charset="utf-8">']
        self.head = self.load_css(style)
        self.head += self.load_js()


class Text(object):
    def __init__(self, output, encoding):
        """ Initialize Text object """
        self.encode_file = True

        # Set the correct output target and create the file if necessary
        if output is None:
            self.file = Terminal()
        else:
            try:
                self.file = codecs.open(output, "w", encoding=encoding)
                self.encode_file = False
            except:
                Logger.Log(str(traceback.format_exc()))
                raise PyMdownFormatterException("Could not open output file!")

    def write(self, text):
        """ Write the content """
        self.file.write(
            text.encode("utf-8", errors="xmlcharrefreplace") if self.encode_file else text
        )

    def close(self):
        """ Close the file """
        self.file.close()
