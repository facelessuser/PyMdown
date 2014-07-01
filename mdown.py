# -*- coding: utf-8 -*-
"""
Mdown

Wraps a https://pypi.python.org/pypi/Markdown
and http://pygments.org/ to perform batch conversion
of markdown files.

Mdown expects a slightly modified version of the
Markdown library to allow for optional highlight.js.

Licensed under MIT
Copyright (c) 2014 Isaac Muse <isaacmuse@gmail.com>
"""
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import print_function
from markdown import markdown
from pygments.formatters import HtmlFormatter
import codecs
import sys
import traceback
import re
from os.path import exists, isfile, dirname, abspath, join

PY3 = sys.version_info >= (3, 0)

if PY3:
    string_type = str
else:
    string_type = basestring  # flake8: noqa

RESOURCE_PATH = abspath(dirname(__file__))


DEFAULT_TEMPLATE = '''<!DOCTYPE html>
<html>
<head>
{{ HEAD }}
</head>
<body>{{ BODY }}</body>
</html>
'''

DEFAULT_CSS = None

RE_PYGMENT_STYLE = r"pygments_style\s*=\s*([a-zA-Z][a-zA-Z_\d]*)"
RE_URL_START = r"https?://"
LOAD_HIGHLIGHT_JS = '<script type="text/javascript">hljs.initHighlightingOnLoad();</script>\n'


def load_text_resource(*args):
    base = None
    try:
        base = sys._MEIPASS
    except:
        base = RESOURCE_PATH

    path = join(base, *args)

    data = None
    if exists(path):
        try:
            with codecs.open(path, "rb") as f:
                data = f.read().decode("utf-8")
        except:
            # print(traceback.format_exc())
            pass
    return data


def get_default_css():
    global DEFAULT_CSS
    if DEFAULT_CSS is None:
        DEFAULT_CSS = load_text_resource("stylesheets", "default.css")
    return "" if DEFAULT_CSS is None else DEFAULT_CSS


def get_default_template():
    return DEFAULT_TEMPLATE


def get_js(js, link=False):
    if link:
        return '<script type="text/javascript" charset="utf-8" src="%s"></script>\n' % js
    else:
        return '<script type="text/javascript">\n%s\n</script>\n' % js


def get_highlight_js_code():
    scripts = []
    try:
        scripts.append(get_js(load_text_resource("highlight.js", "highlight.pack.js")))
        scripts.append(LOAD_HIGHLIGHT_JS)
        # scripts.append(get_js(load_text_resource("highlight.js", "higlight.dynamic.js")))
    except:
        pass
    return scripts


def get_style(style, link=False):
    if link:
        return '<link href="%s" rel="stylesheet" type="text/css">\n' % style
    else:
        return '<style>\n%s\n</style>\n' % style


def get_pygment_style(style):
    try:
        text = HtmlFormatter(style=style).get_style_defs('.codehilite pre')
    except:
        text = HtmlFormatter(style="default").get_style_defs('.codehilite pre')
    return '<style>\n%s\n</style>\n' % text


def get_highlight_js_style(style):
    try:
        text = load_text_resource("highlight.js", "styles", "%s.css" % style)
    except:
        text = load_text_resource("highlight.js", "styles", "%s.css" % style)
    return '<style>\n%s\n</style>\n' % text


class Mdown(object):
    def __init__(self, file_name, encoding, title="Untitled", base_path=None, settings=None):
        self.error = None
        self.settings = settings
        self.file_name = abspath(file_name)
        self.title = title
        self.base_path = base_path if base_path is not None else ''
        self.encoding = encoding
        self.read_extensions()
        self.load_header()
        self.load_body()

    def read_extensions(self):
        extensions = self.settings.get("extensions", "default")
        if isinstance(extensions, string_type) and extensions == "default":
            extensions = [
                "extra",
                "toc",
                "codehilite(guess_lang=False,pygments_style=default)"
            ]
        self.extensions = []
        for e in extensions:
            self.extensions.append(e.replace("${BASE_PATH}", self.base_path))

    def load_highlight(self):
        style = None
        self.highlight_js = self.settings.get("highlight_js", False)
        print(self.highlight_js)
        print(self.settings)
        from markdown.extensions import codehilite
        if not self.highlight_js:
            # Ensure pygments is enabled in the highlighter
            codehilite.pygments = True
            for e in self.extensions:
                if e.startswith("codehilite"):
                    pygment_style = re.search(RE_PYGMENT_STYLE, e)
                    try:
                        style = get_pygment_style("default" if pygment_style is None else pygment_style.group(1))
                    except:
                        self.error = str(traceback.format_exc())
                    break
        else:
            # Disable pygments in the highlighter
            print("disabled")
            codehilite.pygments = False
            for e in self.extensions:
                if e.startswith("codehilite"):
                    try:
                        style = get_highlight_js_style(self.settings.get("highlight_js_theme", "default"))
                    except:
                        self.error = str(traceback.format_exc())
                    break

        css = []
        if style is not None:
            css.append(style)

        return css

    def load_css(self):
        user_css = self.settings.get("css_style_sheet", "default")
        if user_css == "default" or not isinstance(user_css, list):
            css = [get_style(get_default_css())]
        else:
            css = []

            for c in user_css:
                if c == "default":
                    css.append(get_style(get_default_css()))
                if re.match(RE_URL_START, c) is not None:
                    css.append(get_style(c, link=True))
                elif exists(c) and isfile(c):
                    try:
                        with codecs.open(c, "r", "utf-8") as f:
                            css.append(get_style(f.read()))
                    except:
                        self.error = str(traceback.format_exc())

        css += self.load_highlight()
        return ''.join(css)

    def load_js(self):
        user_js = self.settings.get("js_scripts", [])
        scripts = []
        if isinstance(user_js, list) and len(user_js):
            for js in user_js:
                if exists(js):
                    try:
                        with codecs.open(js, "r", encoding="utf-8") as f:
                            scripts.append(
                                get_js(f.read())
                            )
                    except:
                        self.error = str(traceback.format_exc())
                        print(traceback.format_exc())
                else:
                    scripts.append(get_js(js, link=True))
        if self.highlight_js:
            scripts += get_highlight_js_code()
        return ''.join(scripts)

    def load_header(self):
        self.head = '<meta charset="utf-8">\n'
        self.head += self.load_css()
        self.head += self.load_js()
        self.head += '<title>%s</title>\n' % self.title

    def load_body(self):
        self.body = ""
        try:
            with codecs.open(self.file_name, "r", encoding=self.encoding) as f:
                self.body = markdown(f.read(), extensions=self.extensions)
        except:
            self.error = str(traceback.format_exc())

    @property
    def markdown(self):
        self.html_file = None
        html = self.settings.get("html_template", "default")
        if html == "default" or not exists(html):
            html = get_default_template()

        return html.replace(
            "{{ HEAD }}", self.head, 1
        ).replace(
            "{{ BODY }}", self.body, 1
        ).encode("utf-8", errors="xmlcharrefreplace")

    def write(self, output):
        html = self.settings.get("html_template", "default")
        if html == "default" or not exists(html):
            html = get_default_template()

        if output is None:
            self.html_file = None
            return
        try:
            with codecs.open(output, "w", encoding="utf-8", errors="xmlcharrefreplace") as f:
                f.write(
                    html.replace(
                        "{{ HEAD }}", self.head, 1
                    ).replace(
                        "{{ BODY }}", self.body, 1
                    )
                )
            self.html_file = output
        except:
            self.error = str(traceback.format_exc())
            self.html_file = None


class Mdowns(Mdown):
    def __init__(self, string, encoding, title="Untitled", base_path=None, settings=None):
        self.error = None
        self.string = string
        self.encoding = encoding
        self.title = title
        self.base_path = base_path if base_path is not None else ''
        self.settings = settings
        self.read_extensions()
        self.load_header()
        self.load_body()

    def load_body(self):
        self.body = ""
        try:
            self.body = markdown(self.string, extensions=self.extensions)
        except:
            self.error = str(traceback.format_exc())
