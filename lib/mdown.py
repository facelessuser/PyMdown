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
                    ext = self.build_extension(ext, configs.get(ext, []))
                if isinstance(ext, Extension):
                    ext.extendMarkdown(self, globals())
                elif ext is not None:
                    raise TypeError(
                        'Extension "%s.%s" must be of type: "markdown.Extension"'
                        % (ext.__class__.__module__, ext.__class__.__name__))
            except:
                # print(str(traceback.format_exc()))
                continue
        return self


class Mdown(object):
    def __init__(
        self, file_name, encoding, base_path=None, extensions=[]
    ):
        self.file_name = abspath(file_name)
        self.base_path = base_path if base_path is not None else ''
        self.encoding = encoding
        self.read_extensions(extensions)
        self.convert()

    def read_extensions(self, extensions):
        if isinstance(extensions, string_type) and extensions == "default":
            extensions = [
                "extra",
                "toc",
                "codehilite(guess_lang=False,pygments_style=default)"
            ]
        self.extensions = []
        for e in extensions:
            self.extensions.append(e.replace("${BASE_PATH}", self.base_path))

    def convert(self):
        self.markdown = ""
        try:
            with codecs.open(self.file_name, "r", encoding=self.encoding) as f:
                self.markdown = MdWrapper(extensions=self.extensions).convert(f.read())
        except:
            raise MdownException(str(traceback.format_exc()))


class Mdowns(Mdown):
    def __init__(
        self, string,
        base_path=None, extensions=[]
    ):
        self.string = string
        self.base_path = base_path if base_path is not None else ''
        self.read_extensions(extensions)
        self.convert()

    def convert(self):
        self.markdown = ""
        try:
            self.markdown = MdWrapper(extensions=self.extensions).convert(self.string)
        except:
            raise MdownException(str(traceback.format_exc()))
