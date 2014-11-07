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
from markdown.postprocessors import Postprocessor
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
    ] + (['\\'] if _PLATFORM == "windows" else [])
)

RE_TAG_HTML = r'''(?xus)
    (?:
        (?P<comments>(\r?\n?\s*)<!--[\s\S]*?-->(\s*)(?=\r?\n)|<!--[\s\S]*?-->)|
        (?P<open><(?P<tag>(?:%s)))
        (?P<attr>(?:\s+[\w\-:]+(?:\s*=\s*(?:"[^"]*"|'[^']*'))?)*)
        (?P<close>\s*(?:\/?)>)
    )
    '''

RE_TAG_LINK_ATTR = re.compile(
    r'''(?xus)
    (?P<attr>
        (?:
            (?P<name>\s+(?:href|src)\s*=\s*)
            (?P<path>"[^"]*"|'[^']*')
        )
    )
    '''
)


def escape(txt):
    txt = txt.replace('&', '&amp;')
    txt = txt.replace('<', '&lt;')
    txt = txt.replace('>', '&gt;')
    txt = txt.replace('"', '&quot;')
    return txt


def unescape(txt):
    txt = txt.replace('&amp;', '&')
    txt = txt.replace('&lt;', '<')
    txt = txt.replace('&gt;', '>')
    txt = txt.replace('&#39;', "'")
    txt = txt.replace('&quot;', '"')
    return txt


def repl_path(m, base_path):
    """ Replace path with absolute path """

    path = unescape(m.group('path')[1:-1])
    link = m.group(0)
    re_win_drive = re.compile(r"(^[A-Za-z]{1}:(?:\\|/))")

    if (
        not path.startswith(exclusion_list) and
        not (_PLATFORM == "windows" and re_win_drive.match(path) is not None)
    ):
        absolute = normpath(join(base_path, path))
        if exists(absolute):
            link = m.group('name') + "\"" + escape(absolute.replace("\\", "/")) + "\""
    return link


def repl(m, base_path):
    if m.group('comments'):
        tag = m.group('comments')
    else:
        tag = m.group('open')
        tag += RE_TAG_LINK_ATTR.sub(lambda m2: repl_path(m2, base_path), m.group('attr'))
        tag += m.group('close')
    return tag


class AbsolutepathPostprocessor(Postprocessor):
    def run(self, text):
        """ Find and replace paths with absolute paths. """

        basepath = self.config['base_path']
        if basepath:
            tags = re.compile(RE_TAG_HTML % '|'.join(self.config['tags'].split()))

            text = tags.sub(lambda m: repl(m, basepath), text)
        return text


class AbsolutepathExtension(Extension):
    def __init__(self, *args, **kwargs):
        self.config = {
            'base_path': ["", "Base path for absolutepath to use to resolve paths - Default: \"\""],
            'tags': ["img script a link", "tags to convert src and/or href in - Default: 'img scripts a link'"]
        }

        if "base_path" in kwargs and not exists(kwargs["base_path"]):
            del kwargs["base_path"]

        super(AbsolutepathExtension, self).__init__(*args, **kwargs)

    def extendMarkdown(self, md, md_globals):
        """Add AbsolutepathTreeprocessor to Markdown instance"""

        abs_path = AbsolutepathPostprocessor(md)
        abs_path.config = self.getConfigs()
        md.postprocessors.add("absolute-path", abs_path, "_end")
        md.registerExtension(self)


def makeExtension(*args, **kwargs):
    return AbsolutepathExtension(*args, **kwargs)
