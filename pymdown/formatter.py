"""
Formatter.

Places markdown in HTML with the specified CSS and JS etc.

Licensed under MIT
Copyright (c) 2014 - 2015 Isaac Muse <isaacmuse@gmail.com>
"""
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function
import cgi
import codecs
import traceback
import re
import tempfile
import base64
import jinja2
from os import path
from . import util
from . import logger
from . import compat
try:
    from pygments.formatters import get_formatter_by_name
    PYGMENTS_AVAILABLE = True
except Exception:  # pragma: no cover
    PYGMENTS_AVAILABLE = False

RE_URL_START = re.compile(r"^(http|ftp)s?://|tel:|mailto:|data:|news:|#")

image_types = {
    (".png",): "image/png",
    (".jpg", ".jpeg"): "image/jpeg",
    (".gif",): "image/gif"
}


class PyMdownFormatterException(Exception):

    """PyMdown formatter exception."""

    pass


def get_js(js, **kwargs):
    """Get the specified JS code."""

    link = kwargs.get('link', False)
    encoding = kwargs.get('encoding', 'utf-8')

    if link:
        return '<script type="text/javascript" charset="%s" src="%s"></script>\n' % (encoding, js)
    else:
        return '<script type="text/javascript">\n%s\n</script>\n' % js if js is not None else ""


def get_style(style, **kwargs):
    """Get the specified CSS code."""

    link = kwargs.get('link', False)

    if link:
        return '<link href="%s" rel="stylesheet" type="text/css">\n' % style
    else:
        return '<style>\n%s\n</style>\n' % style if style is not None else ""


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

    def __init__(self, encoding):
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

    def __init__(self, encoding='utf-8'):
        """Initialize Text object."""

        self.encode_file = True
        self.file = None
        self.encoding = encoding

    def open(self, output):
        """
        Open output stream.

        Set the correct output target and create the file if necessary.
        """

        if output is None:
            self.file = Terminal(self.encoding)
        else:
            try:
                self.file = codecs.open(output, "w", encoding=self.encoding)
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

        self.settings = kwargs.get("settings", {})
        self.encode_file = True
        self.plain = kwargs.get("plain", False)
        self.template = None
        self.file = None
        self.meta = []
        self.encoding = kwargs.get("encoding", "utf-8")
        self.basepath = kwargs.get("basepath", None)
        self.relative_output = kwargs.get("relative", None)
        self.preview = kwargs.get("preview", False)
        self.aliases = kwargs.get("aliases", [])
        self.template_file = self.settings.get("template", None)
        self.title = "Untitled"
        self.user_path = util.get_user_path()
        self.added_res = set()

    def set_meta(self, meta):
        """Create meta data tags."""

        self.meta = ['<meta charset="%s">' % self.encoding]
        if "title" in meta:
            value = meta["title"]
            if isinstance(value, list):
                if len(value) == 0:
                    value = ""
                else:
                    value = value[0]
            self.title = compat.unicode_type(value)
            del meta["title"]

        for k, v in meta.items():
            if isinstance(v, list):
                v = ','.join(v)
            if v is not None:
                self.meta.append(
                    '<meta name="%s" content="%s">' % (
                        cgi.escape(compat.unicode_type(k), True),
                        cgi.escape(compat.unicode_type(v), True)
                    )
                )

    def get_template_res_path(self, file_name):
        """Get the filepath and absolute filepath of the resource."""

        abs_path = None
        file_path = None
        user_path = util.get_user_path()

        is_abs = util.is_absolute(file_name)

        # Find path relative to basepath or global user path
        # If basepath is defined set paths relative to the basepath if possible
        # or just keep the absolute
        if not is_abs:
            # Is relative path
            if self.basepath is not None:
                base_temp = path.normpath(path.join(self.basepath, file_name))
                if path.exists(base_temp) and path.isfile(base_temp):
                    file_path = base_temp
            if file_path is None and user_path is not None:
                user_temp = path.normpath(path.join(user_path, file_name))
                if path.exists(user_temp) and path.isfile(user_temp):
                    file_path = user_temp

        elif is_abs and path.exists(file_name) and path.isfile(file_name):
            # Is absolute path
            file_path = file_name

        if file_path is not None:
            # Calculate the absolute path
            if is_abs or not self.basepath:
                abs_path = file_path
            else:
                abs_path = path.abspath(path.join(self.basepath, file_path))

            # Adjust path depending on whether we are desiring
            # absolute output or relative output
            if self.settings.get("path_conversion_absolute", True):
                file_path = abs_path
            elif self.relative_output:
                file_path = path.relpath(abs_path, self.relative_output)
        return file_path, abs_path

    def template_embed_image(self, name):
        """Embed an image with base64 encoding."""

        file_name = name.strip()
        file_path, abs_path = self.get_template_res_path(file_name)
        if file_path is not None:
            # If embedding an image, get base64 image type or return path
            ext = path.splitext(file_name)[1]
            embedded = False
            for b64_ext in image_types:
                if ext in b64_ext:
                    try:
                        with open(abs_path, "rb") as f:
                            file_name = "data:%s;base64,%s" % (
                                image_types[b64_ext],
                                base64.b64encode(f.read()).decode('ascii')
                            )
                            embedded = True
                    except Exception:
                        pass
                    break
            if not embedded:
                file_name = ''
        return file_name

    def template_embed_file(self, name, image=False):
        """
        Return the content of the file instead of the file name.

        If "image" is "True", base64 encode the content.
        """

        file_name = name.strip()
        file_name, encoding = util.splitenc(file_name)
        file_path, abs_path = self.get_template_res_path(file_name)
        if file_path is not None:
            if image:
                # If embedding an image, get base64 image type or return path
                ext = path.splitext(file_name)[1]
                embedded = False
                for b64_ext in image_types:
                    if ext in b64_ext:
                        try:
                            with open(abs_path, "rb") as f:
                                file_name = "data:%s;base64,%s" % (
                                    image_types[b64_ext],
                                    base64.b64encode(f.read()).decode('ascii')
                                )
                                embedded = True
                        except Exception:
                            pass
                        break
                if not embedded:
                    file_name = ''
            else:
                file_name = util.load_text_resource(abs_path, encoding=encoding)
                if file_name is None:
                    file_name = ''
        return file_name

    def template_get_path(self, name, quoted=False):
        """Get path in a template."""

        file_name = name.strip()
        file_path = self.get_template_res_path(file_name)[0]
        if file_path is not None:
            file_name = file_path.replace('\\', '/')
            if quoted:
                file_name = compat.pathname2url(file_name)
        return file_name

    def get_template(self):
        """Output the HTML head and body up to the {{ content }} specifier."""
        template = None
        if self.template_file is not None and not self.plain:
            template_path, encoding = util.splitenc(self.template_file)

            if not util.is_absolute(template_path) and self.basepath:
                template_base = path.join(self.basepath, template_path)
            else:
                template_base = ''

            if (
                (not path.exists(template_base) or not path.isfile(template_base)) and
                self.user_path is not None
            ):
                template_path = path.join(self.user_path, template_path)
            else:
                template_path = template_base

            try:
                with codecs.open(template_path, "r", encoding=encoding) as f:
                    template = f.read()
            except Exception:
                logger.Log.error(str(traceback.format_exc()))

        if template is None:
            template = "{{ content }}"
        env = jinja2.Environment()
        env.filters['embed'] = self.template_embed_file
        env.filters['getpath'] = self.template_get_path
        self.template = env.from_string(template)

    def open(self, output):
        """Set and create the output target and target related flags."""

        if output is None:
            self.file = Terminal(self.encoding)
            self.file.name = self.relative_output
        try:
            if not self.preview and output is not None:
                self.file = codecs.open(
                    output, "w",
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

    def write(self, text):
        """Write the given text to the output file."""

        if not self.plain:
            self.load_header(
                self.settings.get("pygments_style", None)
            )

        self.get_template()

        html = self.template.render(
            content=text,
            meta='\n'.join(self.meta) + '\n',
            css=''.join(self.css),
            js=''.join(self.scripts),
            title=cgi.escape(self.title)
        )

        self.file.write(
            html.encode(self.encoding, errors="xmlcharrefreplace") if self.encode_file else html
        )

    def load_highlight(self, highlight_style):
        """Load Syntax highlighter CSS."""

        style = None
        use_pygments_css = bool(self.settings.get("use_pygments_css", True))
        if PYGMENTS_AVAILABLE and highlight_style is not None and use_pygments_css:
            # Ensure pygments is enabled in the highlighter
            style = get_pygment_style(
                highlight_style,
                self.settings.get("pygments_class", "codehilite")
            )

        css = []
        if style is not None:
            css.append(style)

        return css

    def get_res_path(self, resource):
        """Get file path and absolute file path of the file if possible."""

        abs_path = None
        res_path = None

        is_abs = util.is_absolute(resource)
        if not is_abs:
            # Is relative path
            if self.basepath is not None:
                base_temp = path.normpath(path.join(self.basepath, resource))
                if path.exists(base_temp) and path.isfile(base_temp):
                    res_path = resource

            if res_path is None and self.user_path is not None:
                user_temp = path.normpath(path.join(self.user_path, resource))
                if path.exists(user_temp) and path.isfile(user_temp):
                    try:
                        res_path = path.relpath(user_temp, self.basepath) if self.basepath else user_temp
                    except Exception:
                        # No choice but to use absolute path
                        res_path = user_temp
                        is_abs = True

        elif is_abs and path.exists(resource) and path.isfile(resource):
            # Is absolute path
            res_path = path.relpath(resource, self.basepath) if self.basepath else resource

        # Is an existing path.  Make path absolute, relative to output, or leave as is
        # If direct include is not desired, add resource as link.
        if res_path is not None:
            # Calculate the absolute path
            if is_abs or not self.basepath:
                abs_path = res_path
            else:
                abs_path = path.abspath(path.join(self.basepath, res_path))

        return res_path, abs_path

    def convert_path(self, res_path, abs_path, absolute_conversion, omit_conversion):
        """Adjust path depending on whether we are desiring absolute output or relative output."""

        if (self.preview or not omit_conversion):
            if not absolute_conversion and self.relative_output:
                try:
                    res_path = path.relpath(abs_path, self.relative_output)
                except Exception:
                    # No choice put to use absolute path
                    res_path = abs_path
            elif absolute_conversion:
                res_path = abs_path
        return res_path

    def load_resources(self, template_resources, res_get, resources):
        """
        Load the resource (js or css).

            - Resolve whether the path needs to be converted to
              absolute or relative path.
            - See whether we should embed the file's content or
              just add a link to the file.
        """

        if isinstance(template_resources, list) and len(template_resources):
            for pth in template_resources:
                resource = pth
                is_url = RE_URL_START.match(resource)

                # This is a URL, don't include content
                if is_url:
                    resource, encoding = util.splitenc(resource)
                    if resource not in self.added_res:
                        resources.append(res_get(resource, link=True, encoding=encoding))
                        self.added_res.add(resource)
                else:
                    # Find path relative to basepath or global user path
                    # If basepath is defined set paths relative to the basepath if possible
                    # or just keep the absolute

                    # Check for markers
                    direct_include = True
                    omit_conversion = resource.startswith('!')
                    direct_include = resource.startswith('^')

                    if omit_conversion:
                        resource = resource.replace('!', '', 1)
                    elif direct_include:
                        resource = resource.replace('^', '', 1)

                    if not omit_conversion:
                        omit_conversion = self.settings.get("disable_path_conversion", False)

                    absolute_conversion = self.settings.get("path_conversion_absolute", False)

                    resource, encoding = util.splitenc(resource)
                    res_path, abs_path = self.get_res_path(resource)

                    if res_path is not None:
                        res_path = self.convert_path(res_path, abs_path, absolute_conversion, omit_conversion)

                    # We check the absolute path against the current list
                    # and add the respath if not present
                    if abs_path not in self.added_res:
                        if not direct_include:
                            res_path = compat.pathname2url(res_path.replace('\\', '/'))
                            link = True
                        else:
                            res_path = util.load_text_resource(abs_path, encoding=encoding)
                            link = False
                        resources.append(res_get(res_path, link=link, encoding=encoding))
                        self.added_res.add(abs_path)

                    # Not a known path and not a url, just add as is
                    elif resource not in self.added_res:
                        resources.append(
                            res_get(
                                compat.pathname2url(resource.replace('\\', '/')),
                                link=True,
                                encoding=encoding
                            )
                        )
                        self.added_res.add(resource)

    def load_css(self, style):
        """Load specified CSS sources."""

        self.load_resources(self.settings.get("css", []), get_style, self.css)
        for alias in self.aliases:
            key = '@' + alias
            if key in self.settings:
                self.load_resources(
                    self.settings.get(key).get("css"),
                    get_style, self.css
                )
        self.css += self.load_highlight(style)

    def load_js(self):
        """Load specified JS sources."""

        self.load_resources(self.settings.get("js", []), get_js, self.scripts)
        for alias in self.aliases:
            key = '@' + alias
            if key in self.settings:
                self.load_resources(
                    self.settings.get(key).get("js"),
                    get_js, self.scripts
                )

    def load_header(self, style):
        """Load up header related info."""

        self.css = []
        self.scripts = []
        self.load_css(style)
        self.load_js()
