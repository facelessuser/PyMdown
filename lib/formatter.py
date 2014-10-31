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
from os.path import exists, isfile, join, abspath, relpath, dirname
from .resources import load_text_resource, splitenc, get_user_path
from .logger import Logger
try:
    from pygments.formatters import get_formatter_by_name
    pygments = True
except:
    pygments = False
    pass


PY3 = sys.version_info >= (3, 0)

if PY3:
    unicode_string = str
else:
    unicode_string = unicode  # flake8: noqa

RE_URL_START = re.compile(r"https?://")


class PyMdownFormatterException(Exception):
    pass


def get_js(js, link=False, encoding='utf-8'):
    """ Get the specified JS code """
    if link:
        return '<script type="text/javascript" charset="%s" src="%s"></script>\n' % (encoding, js)
    else:
        return '<script type="text/javascript">\n%s\n</script>\n' % js if js is not None else ""


def get_style(style, link=False, encoding=None):
    """ Get the specified CSS code """
    if link:
        return '<link href="%s" rel="stylesheet" type="text/css">\n' % style
    else:
        return '<style>\n%s\n</style>\n' % style if style is not None else ""


def get_pygment_style(style, css_class='codehilite'):
    """ Get the specified pygments sytle CSS """
    try:
        # Try and request pygments to generate it
        text = get_formatter_by_name('html', style=style).get_style_defs('.' + css_class)
    except:
        # Try and request pygments to generate default
        text = get_formatter_by_name('html', style="default").get_style_defs('.' + css_class)
    return '<style>\n%s\n</style>\n' % text if text is not None else ""


class Terminal(object):
    """ Have console output mimic the file output calls """
    name = None

    def write(self, text):
        """ Dump texst to screen """
        if PY3:
            sys.stdout.buffer.write(text)
        else:
            sys.stdout.write(text)

    def close(self):
        """ There is nothing to close """
        pass


class Html(object):
    def __init__(
        self, output, preview=False, title=None, encoding='utf-8',
        plain=False, settings={}
    ):
        self.settings = settings
        self.encode_file = True
        self.body_end = None
        self.no_body = False
        self.plain = plain
        self.template = None
        self.encoding = encoding
        self.template_file = self.settings.get("html_template", None)
        self.title = "Untitled"
        self.user_path = get_user_path()
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
        if (self.template_file is not None):
            template_path, encoding = splitenc(self.template_file)
            if (
                self.user_path is not None and
                (not exists(template_path) or not isfile(template_path))
            ):
                template_path = join(self.user_path, template_path)

            try:
                with codecs.open(template_path, "r", encoding=encoding) as f:
                    self.template = f.read()
            except:
                Logger.error(str(traceback.format_exc()))

        # If template isn't found, we will still output markdown html
        if self.template is not None:
            self.no_body = True
            # We have a template.  Look for {{ BODY }}
            # so we know where to insert the markdown.
            # If we can't find an insertion point, the html
            # will have no markdown content.
            m = re.search(r"\{\{ BODY \}\}", self.template)
            if m:
                self.no_body = False
                meta = '\n'.join(self.meta) + '\n'
                title = '<title>%s</title>\n' % cgi.escape(self.title)
                self.write(
                    self.template[0:m.start(0)].replace(
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
                self.file = codecs.open(output, "w", encoding=self.encoding, errors="xmlcharrefreplace")
                self.encode_file = False
            elif preview:
                self.file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
        except:
            Logger.error(str(traceback.format_exc()))
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
                text.encode(self.encoding, errors="xmlcharrefreplace") if self.encode_file else text
            )

    def load_highlight(self, highlight_style):
        """ Load Syntax highlighter CSS """
        style = None
        if pygments and highlight_style is not None and bool(self.settings.get("use_pygments_css", True)):
            # Ensure pygments is enabled in the highlighter
            style = get_pygment_style(highlight_style, self.settings.get("pygments_class", "codehilite"))

        css = []
        if style is not None:
            css.append(style)

        return css

    def load_resources(self, key, res_get):
        template_resources = self.settings.get(key, [])
        added = set()
        resources = []
        if isinstance(template_resources, list) and len(template_resources):
            for pth in template_resources:
                resource = unicode_string(pth)

                # Check for markers
                relative_path = resource.startswith('&')
                direct_include = not resource.startswith('!')

                # Remove inclusion reject marker
                if not direct_include:
                    resource = resource.replace('!', '', 1)

                # Remove relative path marker
                if relative_path:
                    resource = resource.replace('&', '', 1)
                    direct_include = False

                # Setup paths to check
                resource, encoding = splitenc(resource)
                user_res_path = join(self.user_path, resource) if self.user_path is not None else None
                # Not really the absolute path, but we are tracking absolute paths
                # to reduce duplicate includes, so use the convention with current value as default.
                # If we acquire the real absolute path, we will overwrite this.
                abs_path = resource

                # This is a URL, don't include content
                if RE_URL_START.match(resource) is not None:
                    if abs_path not in added:
                        resources.append(res_get(resource, link=True, encoding=encoding))
                        added.add(abs_path)

                # Do not include content, but we need to resolove the relative path
                elif not direct_include and relative_path:
                    out = self.file.name
                    if out is not None:
                        if exists(resource) and isfile(resource):
                            out = dirname(abspath(out))
                            abs_path = abspath(resource)
                            resource = relpath(abs_path, out).replace('\\', '/')
                        elif user_res_path is not None and exists(user_res_path) and isfile(user_res_path):
                            out = dirname(abspath(out))
                            abs_path = abspath(user_res_path)
                            resource = relpath(abs_path, out).replace('\\', '/')
                    if abs_path not in added:
                        resources.append(res_get(resource, link=True, encoding=encoding))
                        added.add(abs_path)

                # Should not try to include content, just add as a link
                elif not direct_include:
                    if abs_path not in added:
                        resources.append(res_get(resource, link=True, encoding=encoding))
                        added.add(abs_path)

                # The file exists, read content and include
                elif exists(resource) and isfile(resource):
                    # Look at specified location to find the file
                    abs_path = abspath(resource)
                    if abs_path not in added:
                        resources.append(res_get(load_text_resource(resource, encoding=encoding)))
                        added.add(abs_path)

                # The file exists relative to the application, read content and include
                elif user_res_path is not None and exists(user_res_path) and isfile(user_res_path):
                    abs_path = abspath(user_res_path)
                    if abs_path not in added:
                        resources.append(res_get(load_text_resource(user_res_path, encoding=encoding)))
                        added.add(abs_path)

                # Nothing else worked, just include as a link
                else:
                    if abs_path not in added:
                        resources.append(res_get(resource, link=True, encoding=encoding))
                        added.add(abs_path)
        return resources

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
        self.meta = ['<meta charset="%s">' % self.encoding]
        self.head = self.load_css(style)
        self.head += self.load_js()


class Text(object):
    def __init__(self, output, encoding):
        """ Initialize Text object """
        self.encode_file = True
        self.encoding = encoding

        # Set the correct output target and create the file if necessary
        if output is None:
            self.file = Terminal()
        else:
            try:
                self.file = codecs.open(output, "w", encoding=self.encoding)
                self.encode_file = False
            except:
                Logger.error(str(traceback.format_exc()))
                raise PyMdownFormatterException("Could not open output file!")

    def write(self, text):
        """ Write the content """
        self.file.write(
            text.encode(self.encoding, errors="xmlcharrefreplace") if self.encode_file else text
        )

    def close(self):
        """ Close the file """
        self.file.close()
