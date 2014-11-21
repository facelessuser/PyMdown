# -*- coding: utf-8 -*-
"""
mdconverter

Licensed under MIT
Copyright (c) 2014 Isaac Muse <isaacmuse@gmail.com>
"""
from __future__ import unicode_literals
from __future__ import print_function
from markdown import Markdown
import codecs
import sys
import traceback
import re
from . import logger

PY3 = sys.version_info >= (3, 0)
RE_TAGS = re.compile(r'''</?[^>]*>''', re.UNICODE)
RE_WORD = re.compile(r'''[^\w\- ]''', re.UNICODE)
SLUGIFY_EXT = (
    'markdown.extensions.headerid',
    'markdown.extensions.toc',
    'pymdown.headeranchor'
)

if PY3:
    from urllib.parse import quote
    string_type = str
else:
    from urllib import quote
    string_type = basestring  # noqa


def slugify(text, sep):
    """ Custom slugify """
    if text is None:
        return ''
    # Strip html tags and lower
    id = RE_TAGS.sub('', text).lower()
    # Remove non word characters or non spaces and dashes
    # Then convert spaces to dashes
    id = RE_WORD.sub('', id).replace(' ', sep)
    # Encode anything that needs to be
    return quote(id.encode('utf-8'))


class MdConvertException(Exception):
    pass


class MdWrapper(Markdown):
    Meta = {}

    def __init__(self, *args, **kwargs):
        super(MdWrapper, self).__init__(*args, **kwargs)

    def registerExtensions(self, extensions, configs):
        """
        Register extensions with this instance of Markdown.

        Keyword arguments:

        * extensions: A list of extensions, which can either
           be strings or objects.  See the docstring on Markdown.
        * configs: A dictionary mapping module names to config options.

        """
        from markdown import util
        from markdown.extensions import Extension

        for ext in extensions:
            try:
                if isinstance(ext, util.string_type):
                    ext = self.build_extension(ext, configs.get(ext, {}))
                if isinstance(ext, Extension):
                    ext.extendMarkdown(self, globals())
                    logger.Log.debug(
                        'Successfully loaded extension "%s.%s".'
                        % (ext.__class__.__module__, ext.__class__.__name__)
                    )
                elif ext is not None:
                    raise TypeError(
                        'Extension "%s.%s" must be of type: "markdown.Extension"'
                        % (ext.__class__.__module__, ext.__class__.__name__)
                    )
            except:
                # We want to gracefully continue even if an extension fails.
                logger.Log.debug(str(traceback.format_exc()))
                continue

        return self


class MdConvert(object):
    def __init__(self, source, **kwargs):
        """ Initialize """

        base_path = kwargs.get('base_path')
        relative_output = kwargs.get('relative_output')

        self.meta = {}
        self.source = source
        self.base_path = base_path if base_path is not None else ''
        self.relative_output = relative_output if relative_output is not None else ''
        self.encoding = kwargs.get('encoding', 'utf-8')
        self.check_extensions(kwargs.get('extensions', []))
        self.tab_length = kwargs.get('tab_length', 4)
        self.smart_emphasis = kwargs.get('smart_emphasis', True)
        self.lazy_ol = kwargs.get('lazy_ol', True)
        self.enable_attributes = kwargs.get('enable_attributes', True)
        self.output_format = kwargs.get('output_format', 'xhtml1')

    def check_extensions(self, extensions):
        """ Check the extensions and see if anything needs to be modified """
        self.extensions = []
        self.extension_configs = {}
        for e in extensions:
            name = e.get("name", None)
            config = e.get("config", {})
            # Account for no config
            if config is None:
                config = {}
            if name is not None:
                # Use our own slugify
                if name in SLUGIFY_EXT:
                    config['slugify'] = slugify
                # Replace base path keyword
                for k, v in config.items():
                    if isinstance(v, string_type):
                        config[k] = v.replace(
                            '${BASE_PATH}', self.base_path
                        ).replace(
                            '${OUTPUT}', self.relative_output
                        )
                # Add extension
                self.extensions.append(name)
                self.extension_configs[name] = config

    def convert(self):
        """ Convert the file to HTML """
        self.markdown = ""
        try:
            with codecs.open(self.source, "r", encoding=self.encoding) as f:
                md = MdWrapper(
                    extensions=self.extensions,
                    extension_configs=self.extension_configs,
                    smart_emphasis=self.smart_emphasis,
                    tab_length=self.tab_length,
                    lazy_ol=self.lazy_ol,
                    enable_attributes=self.enable_attributes,
                    output_format=self.output_format
                )
                self.markdown = md.convert(f.read())
                try:
                    self.meta = md.Meta
                except:
                    pass
        except:
            raise MdConvertException(str(traceback.format_exc()))


class MdConverts(MdConvert):
    def convert(self):
        """ Convert the given string to HTML """
        self.markdown = ""
        try:
            md = MdWrapper(
                extensions=self.extensions,
                extension_configs=self.extension_configs,
                smart_emphasis=self.smart_emphasis,
                tab_length=self.tab_length,
                lazy_ol=self.lazy_ol,
                enable_attributes=self.enable_attributes,
                output_format=self.output_format
            )
            self.markdown = md.convert(self.source)
            try:
                self.meta = md.Meta
            except:
                pass
        except:
            raise MdConvertException(str(traceback.format_exc()))
