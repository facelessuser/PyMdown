#!/usr/bin/env python
"""
Formatter

Places markdown in HTML with the specified CSS and JS etc.

Licensed under MIT
Copyright (c) 2014 Isaac Muse <isaacmuse@gmail.com>
"""
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function
import cgi
import sys
import codecs
import traceback
import re
import tempfile
from pygments.formatters import get_formatter_by_name
from os.path import exists, isfile, join
from .resources import load_text_resource
from .logger import Logger


PY3 = sys.version_info >= (3, 0)

if PY3:
    unicode_string = str
else:
    unicode_string = unicode  # flake8: noqa

RE_URL_START = r"https?://"


class PyMdownFormatterException(Exception):
    pass


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
        text = get_formatter_by_name('html', style=style).get_style_defs('.codehilite')
    except:
        # Try and request pygments to generate default
        text = get_formatter_by_name('html', style="default").get_style_defs('.codehilite')
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
        plain=False, script_path=None, settings={}
    ):
        self.settings = settings
        self.encode_file = True
        self.body_end = None
        self.no_body = False
        self.plain = plain
        self.template = ''
        self.title = "Untitled"
        self.script_path = script_path
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
        template = self.settings.get("html_template", None)
        app_path = join(self.script_path, template) if self.script_path is not None and template is not None else None
        if template is not None and exists(template) and isfile(template):
            try:
                with codecs.open(template, "r", encoding="utf-8") as f:
                    template = f.read()
            except:
                Logger.log(str(traceback.format_exc()))
        elif app_path is not None and exists(app_path) and isfile(app_path):
            try:
                with codecs.open(app_path, "r", encoding="utf-8") as f:
                    template = f.read()
            except:
                Logger.log(str(traceback.format_exc()))
        self.template = template

        # If template isn't found, we will still output markdown html
        if self.template is not None:
            self.no_body = True
            # We have a template.  Look for {{ BODY }}
            # so we know where to insert the markdown.
            # If we can't find an insertion point, the html
            # will have no markdown content.
            m = re.search(r"\{\{ BODY \}\}", template)
            if m:
                self.no_body = False
                meta = '\n'.join(self.meta) + '\n'
                title = '<title>%s</title>\n' % cgi.escape(self.title)
                self.write(
                    template[0:m.start(0)].replace(
                        "{{ HEAD }}", meta + self.head + title, 1
                    ).replace(
                        "{{ TITLE }}", cgi.escape(self.title)
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
        if not self.no_body:
            self.file.write(
                text.encode("utf-8", errors="xmlcharrefreplace") if self.encode_file else text
            )

    def load_highlight(self, highlight_style):
        """ Load Syntax highlighter CSS """
        style = None
        if highlight_style is not None and bool(self.settings.get("use_pygments_css", True)):
            # Ensure pygments is enabled in the highlighter
            style = get_pygment_style(highlight_style)

        css = []
        if style is not None:
            css.append(style)

        return css

    def load_resources(self, key, res_get):
        user_res = self.settings.get(key, [])
        res = []
        if isinstance(user_res, list) and len(user_res):
            for pth in user_res:
                r = unicode_string(pth)
                app_path = join(self.script_path, r) if self.script_path is not None else None
                direct_include = not r.startswith('!')
                if not direct_include:
                    # Remove inclusion reject marker
                    r = r.replace('!', '', 1)
                if not direct_include or re.match(RE_URL_START, r) is not None:
                    # Don't include content, just reference link
                    res.append(res_get(r, link=True))
                elif exists(r) and isfile(r):
                    # Look at specified location to find the file
                    try:
                        with codecs.open(r, "r", "utf-8") as f:
                            res.append(res_get(f.read()))
                    except:
                        Logger.log(str(traceback.format_exc()))
                elif app_path is not None and exists(app_path) and isfile(app_path):
                    # Look where app binary resides to find the file
                    try:
                        with codecs.open(app_path, "r", "utf-8") as f:
                            res.append(res_get(f.read()))
                    except:
                        Logger.log(str(traceback.format_exc()))
                else:
                    # Could not find file, just add it as a link
                    res.append(res_get(r, link=True))
        return res

    def load_css(self, style):
        """ Load specified CSS sources """
        css = self.load_resources("css_style_sheets", get_style)
        css += self.load_highlight(style)
        return ''.join(css)

    def load_js(self):
        """ Load specified JS sources """
        scripts = self.load_resources("js_scripts", get_js)
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
