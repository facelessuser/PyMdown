"""
pymdown.delete
Really simple plugin to add support for
<ins>test</ins> tags as ^^test^^

MIT license.

Copyright (c) 2014 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from __future__ import unicode_literals
from markdown import Extension
from markdown.inlinepatterns import SimpleTagPattern

RE_SMART_CONTENT = r'((?:[^\^]|\^(?=[^\W_]|\^))+?\^*)'
RE_DUMB_CONTENT = r'((?:[^\^]|(?<!\^)\^(?=[^\W_]|\^))+?)'
RE_SMART_INS_BASE = r'(\^{2})(?![\s\^])%s(?<!\s)\^{2}' % RE_SMART_CONTENT
RE_SMART_INS = r'(?:(?<=_)|(?<![\w\^]))%s(?:(?=_)|(?![\w\^]))' % RE_SMART_INS_BASE
RE_INS_BASE = r'(\^{2})(?!\s)%s(?<!\s)\^{2}' % RE_DUMB_CONTENT
RE_INS = RE_INS_BASE

# (^^^insert^^ at start of superscript) and (^^insert^^ at start of parens to protect against superscript grabbing it)
RE_SMART_SUP = r'(?=(?:\))|(?:\(.*?\)|_|[^\w\^])(?:(?:\(.*?\)|[^\)])+?)\))'
RE_SUP = r'(?=(?:(?:\(.*?\)|[^\)])+?)\))'
RE_SUP_PAREN_INS_BASE = r'(?<=\(\^)%s%s'
RE_PAREN_INS_BASE = r'(?<=\()%s%s'
RE_SMART_SUP_INS = RE_SUP_PAREN_INS_BASE % (RE_SMART_INS_BASE, RE_SMART_SUP)
RE_SMART_SUP_INS2 = RE_PAREN_INS_BASE % (RE_SMART_INS_BASE, RE_SMART_SUP)
RE_SUP_INS = RE_SUP_PAREN_INS_BASE % (RE_INS_BASE, RE_SUP)
RE_SUP_INS2 = RE_PAREN_INS_BASE % (RE_INS_BASE, RE_SUP)


class InsertExtension(Extension):
    """Adds insert extension to Markdown class."""

    def __init__(self, *args, **kwargs):
        self.config = {
            'smart_insert': [True, "Treat ^^connected^^words^^ intelligently - Default: True"]
        }

        super(InsertExtension, self).__init__(*args, **kwargs)

    def extendMarkdown(self, md, md_globals):
        """Add support for <ins>test</ins> tags as ^^test^^"""
        if "^" not in md.ESCAPED_CHARS:
            md.ESCAPED_CHARS.append('^')
        config = self.getConfigs()
        if config.get('smart_insert', True):
            md.inlinePatterns.add("ins", SimpleTagPattern(RE_SMART_INS, "ins"), "<not_strong")
        else:
            md.inlinePatterns.add("ins", SimpleTagPattern(RE_INS, "ins"), "<not_strong")

        self.md = md
        md.registerExtension(self)

    def reset(self):
        if "sup" in self.md.inlinePatterns.keys():
            config = self.getConfigs()
            if config.get('smart_insert', True):
                self.md.inlinePatterns.add("sup-ins", SimpleTagPattern(RE_SMART_SUP_INS, "ins"), "<sup")
                self.md.inlinePatterns.add("sup-ins2", SimpleTagPattern(RE_SMART_SUP_INS2, "ins"), "<sup-ins")
            else:
                self.md.inlinePatterns.add("sup-ins", SimpleTagPattern(RE_SUP_INS, "ins"), "<sup")
                self.md.inlinePatterns.add("sup-ins2", SimpleTagPattern(RE_SUP_INS2, "ins"), "<sup-ins")


def makeExtension(*args, **kwargs):
    return InsertExtension(*args, **kwargs)
