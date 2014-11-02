"""
pymdown.relativepath
An extension for Python Markdown.
Given an absolute base path, this extension searches for file
references that are relative and converts them to a path relative
to the base path.

MIT license.

Copyright (c) 2014 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from __future__ import unicode_literals
from markdown import Extension
from markdown.treeprocessors import Treeprocessor
from os.path import exists, normpath, join, relpath
import re
import sys

if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":
    _PLATFORM = "osx"
else:
    _PLATFORM = "linux"

exclusion_list = tuple(
    [
        'https://', 'http://', '#',
        "data:image/jpeg;base64,", "data:image/png;base64,", "data:image/gif;base64,"
    ] + (['\\'] if _PLATFORM == "windows" else [])
)

absolute_list = tuple(
    [
        'file://', '/'
    ] + (['\\'] if _PLATFORM == "windows" else [])
)

RE_WIN_DRIVE = re.compile(r"(^(?P<drive>[A-Za-z]{1}):(?:\\|/))")


def repl(path, base_path, relative_path):
    """ Replace path with absolute path """

    link = path
    convert = False
    abs_path = None

    if (not path.startswith(exclusion_list)):
        abs_path = path
        if (
            not path.startswith(absolute_list) and
            not (_PLATFORM == "windows" and RE_WIN_DRIVE.match(path) is not None)
        ):
            # Convert current relative path to absolute
            absolute = normpath(join(base_path, path))
            if exists(absolute):
                abs_path = absolute.replace("\\", "/")
            else:
                return link
        else:
            # Strip 'file://'
            if path.startswith('file://'):
                abs_path = path.replace('file://', '', 1)
            else:
                abs_path = path
        if (_PLATFORM == "windows"):
            # Make sure basepath starts with same drive location as target
            # If they don't match, we will stay with absolute path.
            if (base_path.startswith('//') and base_path.startswith('//')):
                convert = True
            else:
                base_drive = RE_WIN_DRIVE.match(base_path)
                path_drive = RE_WIN_DRIVE.match(abs_path)
                if (
                    (base_drive and path_drive) and
                    base_drive.group('drive').lower() == path_drive.group('drive').lower()
                ):
                    convert = True
        else:
            # OSX and Linux
            convert = True

        if convert:
            # Convert path relative to the base path
            link = relpath(abs_path, relative_path).replace('\\', '/')
        else:
            # We have an absolute path, but we can't make it relative
            # to base path, so we will just use the absolute.
            link = abs_path

    return link


class RelativePathTreeprocessor(Treeprocessor):
    def run(self, root):
        """ Replace paths with relative to base path """

        basepath = self.config['base_path']
        relativepath = self.config['relative_path']
        if basepath and relativepath:
            for tag in root.getiterator():
                if tag.tag in self.config['tags'].split():
                    src = tag.attrib.get("src")
                    href = tag.attrib.get("href")
                    if src is not None:
                        tag.attrib["src"] = repl(src, basepath, relativepath)
                    if href is not None:
                        tag.attrib["href"] = repl(href, basepath, relativepath)
        return root


class RelativePathExtension(Extension):
    def __init__(self, *args, **kwargs):
        self.config = {
            'base_path': ["", "Base path used to find files - Default: \"\""],
            'relative_path': ["", "Path that files will be relative to - Default: \"\""],
            'tags': ["img script a link", "tags to convert src and/or href in - Default: 'img scripts a link'"]
        }

        if "base_path" in kwargs and not exists(kwargs["base_path"]):
            del kwargs["base_path"]
        if "relative_path" in kwargs and not exists(kwargs['relative_path']):
            del kwargs["relative_path"]

        super(RelativePathExtension, self).__init__(*args, **kwargs)

    def extendMarkdown(self, md, md_globals):
        """Add RelativePathTreeprocessor to Markdown instance"""

        abs_path = RelativePathTreeprocessor(md)
        abs_path.config = self.getConfigs()
        md.treeprocessors.add("relative-path", abs_path, "_end")
        md.registerExtension(self)


def makeExtension(*args, **kwargs):
    return RelativePathExtension(*args, **kwargs)
