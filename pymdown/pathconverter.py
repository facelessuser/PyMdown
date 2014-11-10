"""
pymdown.pathconverter
An extension for Python Markdown.

An extension to covert tag paths to relative or absolute:

Given an absolute base and a target relative path, this extension searches for file
references that are relative and converts them to a path relative
to the base path.

-or-

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


def repl_relative(m, base_path, relative_path):
    """ Replace path with relative path """

    path = unescape(m.group('path')[1:-1])
    link = m.group(0)
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
            link = m.group('name') + "\"" + escape(relpath(abs_path, relative_path).replace('\\', '/')) + "\""
        else:
            # We have an absolute path, but we can't make it relative
            # to base path, so we will just use the absolute.
            link = m.group('name') + "\"" + escape(abs_path) + "\""

    return link


def repl_absolute(m, base_path):
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


def repl(m, base_path, rel_path=None):
    if m.group('comments'):
        tag = m.group('comments')
    else:
        tag = m.group('open')
        if rel_path is None:
            tag += RE_TAG_LINK_ATTR.sub(lambda m2: repl_absolute(m2, base_path), m.group('attr'))
        else:
            tag += RE_TAG_LINK_ATTR.sub(lambda m2: repl_relative(m2, base_path, rel_path), m.group('attr'))
        tag += m.group('close')
    return tag


class PathConverterPostprocessor(Postprocessor):
    def run(self, text):
        """ Finds and converts paths. """

        basepath = self.config['base_path']
        relativepath = self.config['relative_path']
        absolute = bool(self.config['absolute'])
        tags = re.compile(RE_TAG_HTML % '|'.join(self.config['tags'].split()))
        if not absolute and basepath and relativepath:
            text = tags.sub(lambda m: repl(m, basepath, relativepath), text)
        elif absolute and basepath:
            text = tags.sub(lambda m: repl(m, basepath), text)
        return text


class PathConverterExtension(Extension):
    def __init__(self, *args, **kwargs):
        self.config = {
            'base_path': ["", "Base path used to find files - Default: \"\""],
            'relative_path': ["", "Path that files will be relative to (not needed if using absolute) - Default: \"\""],
            'absolute': [True, "Paths are absolute by default; disable for relative - Default: True"],
            'tags': ["img script a link", "tags to convert src and/or href in - Default: 'img scripts a link'"]
        }

        if "base_path" in kwargs and not exists(kwargs["base_path"]):
            del kwargs["base_path"]
        if "relative_path" in kwargs and not exists(kwargs['relative_path']):
            del kwargs["relative_path"]

        super(PathConverterExtension, self).__init__(*args, **kwargs)

    def extendMarkdown(self, md, md_globals):
        """Add PathConverterPostprocessor to Markdown instance"""

        rel_path = PathConverterPostprocessor(md)
        rel_path.config = self.getConfigs()
        md.postprocessors.add("path-converter", rel_path, "_end")
        md.registerExtension(self)


def makeExtension(*args, **kwargs):
    return PathConverterExtension(*args, **kwargs)
