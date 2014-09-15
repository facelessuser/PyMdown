"""
mdownx.smartsymbols
Really simple plugin to add support for
  copyright, trademark, and registered symbols
  plus/minus

MIT license.

Copyright (c) 2014 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from __future__ import unicode_literals
from markdown import Extension
from markdown.inlinepatterns import HtmlPattern
from markdown.odict import OrderedDict
from markdown.treeprocessors import InlineProcessor

RE_TRADE = ("smarttrademark", r'\(tm\)', r'&trade;')
RE_COPY = ("smartcopyright", r'\(c\)', r'&copy;')
RE_REG = ("smartregistered", r'\(r\)', r'&reg;')
RE_PLUSMINUS = ("smartplusminus", r'\+/\-', r'&plusmn;')

REPL = {
    'trademark': RE_TRADE,
    'copyright': RE_COPY,
    'registered': RE_REG,
    'plusminus': RE_PLUSMINUS
}


class SmartSymbolsPattern(HtmlPattern):
    def __init__(self, pattern, replace, md):
        """ Setup replace pattern """
        super(SmartSymbolsPattern, self).__init__(pattern)
        self.replace = replace
        self.md = md

    def handleMatch(self, m):
        """ Replace symbol """
        return self.md.htmlStash.store(m.expand(self.replace), safe=True)


class SmartSymbolsExtension(Extension):
    def __init__(self, *args, **kwargs):
        """ Setup config of which symbols are enabled """
        self.config = {
            'trademark': [True, 'Trademark'],
            'copyright': [True, 'Copyright'],
            'registered': [True, 'Registered'],
            'plusminus': [True, 'Plus/Minus']
        }
        super(SmartSymbolsExtension, self).__init__(*args, **kwargs)

    def add_pattern(self, patterns, md):
        """ Construct the inline symbol pattern """
        self.patterns.add(
            patterns[0],
            SmartSymbolsPattern(patterns[1], patterns[2], md),
            '_begin'
        )

    def extendMarkdown(self, md, md_globals):
        """ Create a dict of inline replace patterns and add to the treeprocessor """
        configs = self.getConfigs()
        self.patterns = OrderedDict()
        for k, v in REPL.items():
            if configs[k]:
                self.add_pattern(v, md)

        inlineProcessor = InlineProcessor(md)
        inlineProcessor.inlinePatterns = self.patterns
        md.treeprocessors.add('smartsymbols', inlineProcessor, '_end')


def makeExtension(*args, **kwargs):
    return SmartSymbolsExtension(*args, **kwargs)
