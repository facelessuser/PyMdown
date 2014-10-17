"""
pymdown.absolutepath
An extension for Python Markdown.
Given an absolute base path, this extension searches for file
references that are relative and converts them to absolute paths.

MIT license.

Copyright (c) 2014 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from __future__ import unicode_literals
from markdown import Extension
from markdown.treeprocessors import Treeprocessor
from os.path import exists, normpath, join
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
        'file://', 'https://', 'http://', '/', '#',
        "data:image/jpeg;base64,", "data:image/png;base64,", "data:image/gif;base64,"
    ] + ['\\'] if _PLATFORM == "windows" else []
)


def repl(path, base_path):
    """ Replace path with absolute path """

    link = path
    re_win_drive = re.compile(r"(^[A-Za-z]{1}:(?:\\|/))")

    if (
        not path.startswith(exclusion_list) and
        not (_PLATFORM == "windows" and re_win_drive.match(path) is not None)
    ):
        absolute = normpath(join(base_path, path))
        if exists(absolute):
            link = absolute.replace("\\", "/")
    return link


class AbsolutepathTreeprocessor(Treeprocessor):
    def run(self, root):
        """ Replace relative paths with absolute """

        if self.config['base_path'] is "":
            return root

        for tag in root.getiterator():
            if tag.tag in ("img", "scripts", "a", "link"):
                src = tag.attrib.get("src")
                href = tag.attrib.get("href")
                if src is not None:
                    tag.attrib["src"] = repl(src, self.config['base_path'])
                if href is not None:
                    tag.attrib["href"] = repl(href, self.config['base_path'])
        return root


class AbsolutepathExtension(Extension):
    def __init__(self, *args, **kwargs):
        self.config = {
            'base_path': ["", "Base path for absolute path to use to resolve paths - Default: \"\""]
        }

        if "base_path" in kwargs and not exists(kwargs["base_path"]):
            del kwargs["base_path"]

        super(AbsolutepathExtension, self).__init__(*args, **kwargs)

    def extendMarkdown(self, md, md_globals):
        """Add AbsolutepathTreeprocessor to Markdown instance"""

        abs_path = AbsolutepathTreeprocessor(md)
        abs_path.config = self.getConfigs()
        md.treeprocessors.add("absolute-path", abs_path, "_end")
        md.registerExtension(self)


def makeExtension(*args, **kwargs):
    return AbsolutepathExtension(*args, **kwargs)
