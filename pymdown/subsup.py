"""
pymdown.delete
Really simple plugin to add support for
Test<sub>sub</sub> via Test(~sub) and Test<sup>super</sup> via Test(^super)

MIT license.

Copyright (c) 2014 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from __future__ import unicode_literals
from markdown import Extension
from markdown.inlinepatterns import SimpleTagPattern

RE_SUPER = r'(\(\^)((?:\(.*?\)|[^\)])+?)\)'
RE_SUB = r'(\(~)((?:\(.*?\)|[^\)])+?)\)'


class ScriptExtension(Extension):
    """Adds delete extension to Markdown class."""

    def __init__(self, *args, **kwargs):
        self.config = {
            'subscript': [True, "Enable subscript - Default: True"],
            'superscript': [True, "Enable superscript - Default: True"]
        }

        super(ScriptExtension, self).__init__(*args, **kwargs)

    def extendMarkdown(self, md, md_globals):
        """Add support for <sub>test</sub> and <sup>test</sup> """
        config = self.getConfigs()
        if "^" not in md.ESCAPED_CHARS:
            md.ESCAPED_CHARS.append('^')
        if "~" not in md.ESCAPED_CHARS:
            md.ESCAPED_CHARS.append('~')
        if config.get('subscript', True):
            md.inlinePatterns.add("sub", SimpleTagPattern(RE_SUB, "sub"), ">entity")
        if config.get('superscript', True):
            md.inlinePatterns.add("sup", SimpleTagPattern(RE_SUPER, "sup"), ">entity")


def makeExtension(*args, **kwargs):
    return ScriptExtension(*args, **kwargs)
