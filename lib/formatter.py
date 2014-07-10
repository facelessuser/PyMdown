from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
import codecs
import traceback
import re
from .resources import load_text_resource
from .logger import Logger
from pygments.formatters import HtmlFormatter
from os.path import exists, isfile
import tempfile

DEFAULT_TEMPLATE = '''<!DOCTYPE html>
<html>
<head>
{{ HEAD }}
</head>
<body>{{ BODY }}</body>
</html>
'''

DEFAULT_CSS = None
RE_URL_START = r"https?://"


class MdownFormatterException(Exception):
    pass


def get_default_template():
    return DEFAULT_TEMPLATE


def get_default_css():
    global DEFAULT_CSS
    if DEFAULT_CSS is None:
        DEFAULT_CSS = load_text_resource("stylesheets", "default.css")
    return "" if DEFAULT_CSS is None else DEFAULT_CSS


def get_js(js, link=False):
    if link:
        return '<script type="text/javascript" charset="utf-8" src="%s"></script>\n' % js
    else:
        return '<script type="text/javascript">\n%s\n</script>\n' % js if js is not None else ""


def get_style(style, link=False):
    if link:
        return '<link href="%s" rel="stylesheet" type="text/css">\n' % style
    else:
        return '<style>\n%s\n</style>\n' % style if style is not None else ""


def get_pygment_style(style):
    try:
        # Try and request pygments to generate it
        text = HtmlFormatter(style=style).get_style_defs('.codehilite pre')
    except:
        # Try and request pygments to generate default
        text = HtmlFormatter(style="default").get_style_defs('.codehilite pre')
    return '<style>\n%s\n</style>\n' % text if text is not None else ""


class Terminal(object):
    name = None

    def write(self, text):
        print(text.encode("utf-8", errors="xmlcharrefreplace"))

    def close(self):
        pass


class Html(object):
    def __init__(self, output, preview=False, title=None, plain=False, settings={}):
        self.settings = settings
        self.encode_file = True
        self.body_end = None
        self.template = ''
        self.set_output(output, preview)
        self.load_header(
            self.settings.get("style", None),
            title if title is not None else "Untitled"
        )
        if not plain:
            self.write_html_start()

    def write_html_start(self):
        template = self.settings.get("html_template", "default")
        if template == "default" or not exists(template):
            template = get_default_template()
        self.template = template

        if self.template != "":
            m = re.search(r"\{\{ BODY \}\}", template)
            if m:
                self.write(template[0:m.start(0)].replace("{{ HEAD }}", self.head, 1))
                self.body_end = m.end(0)

    def set_output(self, output, preview):
        print(output)
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
            raise MdownFormatterException("Could not open output file!")

    def close(self):
        if self.body_end is not None:
            self.write(self.template[self.body_end:])
        self.file.close()

    def write(self, text):
        self.file.write(
            text.encode("utf-8", errors="xmlcharrefreplace") if self.encode_file else text
        )

    def load_highlight(self, highlight_style):
        style = None
        self.highlight_enabled = False
        if highlight_style is not None:
            self.highlight_enabled = True
            # Ensure pygments is enabled in the highlighter
            style = get_pygment_style(highlight_style)

        css = []
        if style is not None:
            css.append(style)

        return css

    def load_css(self, style):
        user_css = self.settings.get("css_style_sheets", "default")
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
                        Logger.log(str(traceback.format_exc()))

        css += self.load_highlight(style)
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
                        Logger.log(str(traceback.format_exc()))
                else:
                    scripts.append(get_js(js, link=True))
        return ''.join(scripts)

    def load_header(self, style, title):
        self.head = '<meta charset="utf-8">\n'
        self.head += self.load_css(style)
        self.head += self.load_js()
        self.head += '<title>%s</title>\n' % title


class Text(object):
    def __init__(self, output, encoding):
        self.encode_file = True
        if output is None:
            self.file = Terminal()
        else:
            try:
                self.file = codecs.open(output, "w", encoding=encoding)
                self.encode_file = False
            except:
                Logger.Log(str(traceback.format_exc()))
                raise MdownFormatterException("Could not open output file!")

    def write(self, text):
        self.file.write(
            text.encode("utf-8", errors="xmlcharrefreplace") if self.encode_file else text
        )

    def close(self):
        self.file.close()
