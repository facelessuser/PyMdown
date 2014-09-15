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
from __future__ import print_function
from markdown import Markdown
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


class MdownException(Exception):
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
        import logging

        logger =  logging.getLogger('MARKDOWN')

        for ext in extensions:
            try:
                if isinstance(ext, util.string_type):
                    ext = self.build_extension(ext, configs.get(ext, {}))
                if isinstance(ext, Extension):
                    ext.extendMarkdown(self, globals())
                    logger.info('Successfully loaded extension "%s.%s".'
                                % (ext.__class__.__module__, ext.__class__.__name__))
                elif ext is not None:
                    raise TypeError(
                        'Extension "%s.%s" must be of type: "markdown.Extension"'
                        % (ext.__class__.__module__, ext.__class__.__name__))
            except:
                print(str(traceback.format_exc()))
                continue

        return self


class Mdown(object):
    def __init__(
        self, file_name, encoding, base_path=None, extensions=[]
    ):
        """ Initialize """
        self.meta = {}
        self.file_name = abspath(file_name)
        self.base_path = base_path if base_path is not None else ''
        self.encoding = encoding
        self.check_extensions(extensions)
        self.convert()

    def check_extensions(self, extensions):
        """ Check the extensions and see if anything needs to be modified """
        if isinstance(extensions, string_type) and extensions == "default":
            extensions = [
                "markdown.extensions.extra",
                "markdown.extensions.toc",
                "markdown.extensions.codehilite(guess_lang=False,pygments_style=default)"
            ]
        self.extensions = []
        for e in extensions:
            self.extensions.append(e.replace("${BASE_PATH}", self.base_path))

    def convert(self):
        """ Convert the file to HTML """
        self.markdown = ""
        try:
            with codecs.open(self.file_name, "r", encoding=self.encoding) as f:
                md = MdWrapper(extensions=self.extensions)
                self.markdown = md.convert(f.read())
                try:
                    self.meta = md.Meta
                except:
                    pass
        except:
            raise MdownException(str(traceback.format_exc()))


class Mdowns(Mdown):
    def __init__(
        self, string,
        base_path=None, extensions=[]
    ):
        """ Initialize """
        self.meta = {}
        self.string = string
        self.base_path = base_path if base_path is not None else ''
        self.check_extensions(extensions)
        self.convert()

    def convert(self):
        """ Convert the given string to HTML """
        self.markdown = ""
        try:
            md = MdWrapper(extensions=self.extensions)
            self.markdown = md.convert(self.string)
            try:
                self.meta = md.Meta
            except:
                pass
        except:
            raise MdownException(str(traceback.format_exc()))
