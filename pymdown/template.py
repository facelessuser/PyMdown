"""
Template.

Places markdown in HTML with the specified CSS and JS etc.

Licensed under MIT
Copyright (c) 2014 - 2015 Isaac Muse <isaacmuse@gmail.com>
"""
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function
import jinja2
from os import path
from . import util
import codecs
import cgi
import traceback
from . import logger
from . import compat
import base64
import re

image_types = {
    (".png",): "image/png",
    (".jpg", ".jpeg"): "image/jpeg",
    (".gif",): "image/gif"
}

RE_URL_START = re.compile(r"^(http|ftp)s?://|tel:|mailto:|data:|news:|#")


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


class Template(object):
    """Class for handling templates."""

    def __init__(self, **kwargs):
        """Initialize."""

        self.basepath = kwargs.get('basepath')
        self.relpath = kwargs.get('relpath')
        self.userpath = util.get_user_path()
        self.force_conversion = kwargs.get('force_conversion', False)
        self.disable_path_conversion = kwargs.get('disable_path_conversion', False)
        self.absolute_path_conversion = kwargs.get('absolute_path_conversion', False)

        # Setup template environment
        template_tags = kwargs.get('template_tags', {})
        block_tags = template_tags.get('block', ('{%', '%}'))
        variable_tags = template_tags.get('variable', ('{{', '}}'))
        comment_tags = template_tags.get('comment', ('{#', '#}'))
        self.env = jinja2.Environment(
            block_start_string=block_tags[0],
            block_end_string=block_tags[1],
            variable_start_string=variable_tags[0],
            variable_end_string=variable_tags[1],
            comment_start_string=comment_tags[0],
            comment_end_string=comment_tags[1]
        )
        self.env.filters['embedimage'] = self.embed_image
        self.env.filters['getpath'] = self.get_path
        self.env.filters['getpathurl'] = self.get_path_url
        self.env.filters['getcss'] = self.get_css
        self.env.filters['getjs'] = self.get_js
        self.env.filters['gettxt'] = self.get_txt
        self.env.filters['getmeta'] = self.get_meta

    def get_template(self, template_file):
        """Output the HTML head and body up to the {{ content }} specifier."""

        template = None
        if template_file is not None:
            template_path, encoding = util.splitenc(template_file)

            if not util.is_absolute(template_path) and self.basepath:
                template_base = path.join(self.basepath, template_path)
            else:
                template_base = ''

            if (
                (not path.exists(template_base) or not path.isfile(template_base)) and
                self.userpath is not None
            ):
                template_path = path.join(self.userpath, template_path)
            else:
                template_path = template_base

            try:
                with codecs.open(template_path, "r", encoding=util._get_encoding(encoding)) as f:
                    template = f.read()
            except Exception:
                logger.Log.error(str(traceback.format_exc()))

        return self.env.from_string('{{ page.content }}' if template is None else template)

    def get_template_from_string(self, text):
        """Get the template from the provided string."""

        return self.env.from_string(text)

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
            if self.absolute_path_conversion:
                file_path = abs_path
            elif self.relpath:
                file_path = path.relpath(abs_path, self.relpath)
        return file_path, abs_path

    def get_path_url(self, name):
        """Get url from path in a template that is also quoted."""

        return compat.pathname2url(self.get_path(name))

    def get_path(self, name):
        """Get path in a template."""

        file_name = name.strip()
        file_path = self.get_template_res_path(file_name)[0]
        if file_path is not None:
            file_name = file_path.replace('\\', '/')
        return file_name

    def embed_image(self, name):
        """
        Return the content of the file instead of the file name.

        If "image" is "True", base64 encode the content.
        """

        file_name = name.strip()
        file_name = util.splitenc(file_name)[0]
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

            if res_path is None and self.userpath is not None:
                user_temp = path.normpath(path.join(self.userpath, resource))
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

    def convert_path(self, res_path, abs_path, omit_conversion):
        """Adjust path depending on whether we are desiring absolute output or relative output."""

        if (self.force_conversion or not omit_conversion):
            if not self.absolute_path_conversion and self.relpath:
                try:
                    res_path = path.relpath(abs_path, self.relpath)
                except Exception:
                    # No choice put to use absolute path
                    res_path = abs_path
            elif self.absolute_path_conversion:
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
                    resources.append(res_get(resource, link=True, encoding=encoding))
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
                        omit_conversion = self.disable_path_conversion

                    resource, encoding = util.splitenc(resource)
                    res_path, abs_path = self.get_res_path(resource)

                    if res_path is not None:
                        res_path = self.convert_path(res_path, abs_path, omit_conversion)

                    # We check the absolute path against the current list
                    # and add the respath if not present
                    if res_path:
                        if not direct_include:
                            res_path = compat.pathname2url(res_path.replace('\\', '/'))
                            link = True
                        else:
                            res_path = util.load_text_resource(abs_path, encoding=encoding)
                            link = False
                        resources.append(res_get(res_path, link=link, encoding=encoding))

                    # Not a known path and not a url, just add as is
                    else:
                        resources.append(
                            res_get(
                                compat.pathname2url(resource.replace('\\', '/')),
                                link=True,
                                encoding=encoding
                            )
                        )

    def load_css_files(self, styles):
        """Load specified CSS sources."""

        css = []
        self.load_resources(styles, get_style, css)
        return css

    def load_js_files(self, js):
        """Load specified JS sources."""

        scripts = []
        self.load_resources(js, get_js, scripts)
        return scripts

    def load_txt_files(self, text):
        """Load specified text sources."""

        texts = []
        for t in text:
            t, encoding = util.splitenc(t)
            res_path, abs_path = self.get_res_path(t)

            if res_path is not None:
                texts.append(util.load_text_resource(abs_path, encoding=encoding))
        return texts

    def get_css(self, css):
        """Load a css source or sources."""

        files = []
        if isinstance(css, compat.string_type):
            files = self.load_css_files([css])
        elif isinstance(css, list):
            files = self.load_css_files(css)

        return ''.join(files) if len(files) else ''

    def get_js(self, js):
        """Load a javascript source or sources."""

        files = []
        if isinstance(js, compat.string_type):
            files = self.load_js_files([js])
        elif isinstance(js, list):
            files = self.load_js_files(js)

        return ''.join(files) if len(files) else ''

    def get_txt(self, text):
        """Load a markdown source or sources."""

        files = []
        if isinstance(text, compat.string_type):
            files = self.load_txt_files([text])
        elif isinstance(text, list):
            files = self.load_txt_files(text)

        return ''.join(files) if len(files) else ''

    def get_meta(self, value, name="name"):
        """Create meta tag."""

        meta_value = None
        meta_name = None
        if isinstance(name, compat.string_type):
            meta_name = cgi.escape(name, True)
        if isinstance(value, compat.string_type):
            meta_value = cgi.escape(value, True)
        elif isinstance(value, list):
            try:
                meta_value = cgi.escape(', '.join(value), True)
            except Exception:
                pass

        meta = ''
        if meta_value and meta_name:
            meta = '<meta name="%s" value="%s">' % (meta_name, meta_value)
        return meta
