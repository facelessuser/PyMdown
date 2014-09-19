"""
mdownx.betterem
Add inteligent handling of to em and strong notations

MIT license.

Copyright (c) 2014 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from __future__ import absolute_import
from __future__ import unicode_literals
from markdown import Extension
from markdown.inlinepatterns import SimpleTagPattern, DoubleTagPattern
from markdown import util

SMART_STAR_EMPHASIS_RE = r'(?<![a-zA-Z\d*])(\*)(?![\*\s])(.+?\**?)(?<!\s)\2(?![a-zA-Z\d*])'
SMART_STAR_STRONG_RE = r'(?<![a-zA-Z\d*])(\*{2})(?![\*\s])(.+?\**?)(?<!\s)\2(?![a-zA-Z\d*])'
SMART_STAR_TRIPLE_RE = r'(?<![a-zA-Z\d*])(\*{3})(?![\*\s])(.+?\**?)(?<!\s)\2(?![a-zA-Z\d*])'
SMART_UNDERLINE_EMPHASIS_RE = r'(?<![a-zA-Z\d_])(_)(?![_\s])(.+?_*?)(?<!\s)\2(?![a-zA-Z\d_])'
SMART_UNDERLINE_STRONG_RE = r'(?<![a-zA-Z\d_])(_{2})(?![_\s])(.+?_*?)(?<!\s)\2(?![a-zA-Z\d_])'
SMART_UNDERLINE_TRIPLE_RE = r'(?<![a-zA-Z\d_])(_{3})(?![_\s])(.+?_*?)(?<!\s)\2(?![a-zA-Z\d_])'

STAR_TRIPLE_RE = r'(\*{3})(?!\s)(.+?)(?<!\s)\2'
UNEVEN_STAR321 = r'(\*{3})(?!\s)(.+?)(?<!\s)\*{2}(.+?)(?<!\s)\*'
UNEVEN_STAR312 = r'(\*{3})(?!\s)(.+?)(?<!\s)\*(.+?)(?<!\s)\*{2}'
STAR_STRONG_RE = r'(\*{2})(?!\s)(.+?)(?<!\s)\2'
STAR_EMPHASIS_RE = r'(\*)(?!\s)(.+?)(?<!\s)\2'

UNDERLINE_TRIPLE_RE = r'(_{3})(?!\s)(.+?)(?<!\s)\2'
UNEVEN_UNDERSCORE321 = r'(_{3})(?!\s)(.+?)(?<!\s)_{2}(.+?)(?<!\s)_'
UNEVEN_UNDERSCORE312 = r'(_{3})(?!\s)(.+?)(?<!\s)_(.+?)(?<!\s)_{2}'
UNDERLINE_STRONG_RE = r'(_{2})(?!\s)(.+?)(?<!\s)\2'
UNDERLINE_EMPHASIS_RE = r'(_)(?!\s)(.+?)(?<!\s)\2'

smart_enable_keys = [
    "all", "asterisk", "underscore", "none"
]


class BetterDoubleTagPattern(SimpleTagPattern):
    """Return a ElementTree element nested in tag2 nested in tag1.

    Useful for strong emphasis etc.

    """
    def handleMatch(self, m):
        tag1, tag2 = self.tag.split(",")
        el1 = util.etree.Element(tag1)
        el2 = util.etree.SubElement(el1, tag2)
        el2.text = m.group(3)
        el2.tail = m.group(4)
        return el1


class BetterEmExtension(Extension):
    """ Add extension to Markdown class."""

    def __init__(self, *args, **kwargs):
        self.config = {
            'smart_enable': ["all", "Treat connected words intelligently - Default: all"]
        }

        if "smart_enable" in kwargs and kwargs["smart_enable"] not in smart_enable_keys:
            del kwargs["smart_enable"]

        super(BetterEmExtension, self).__init__(*args, **kwargs)

    def extendMarkdown(self, md, md_globals):
        """ Modify inline patterns. """

        self.md = md
        self.load = True
        md.registerExtension(self)

    def make_better(self):
        """
        This should work with the default smart_strong package enabled or disabled.
        """

        config = self.getConfigs()
        enabled = config["smart_enable"]
        if enabled:
            enable_all = enabled == "all"
            enable_underscore = enabled == "underscore"
            enable_asterisk = enabled == "asterisk"

        star_triple = SMART_STAR_TRIPLE_RE if enable_all or enable_asterisk else STAR_TRIPLE_RE
        star_double = SMART_STAR_STRONG_RE if enable_all or enable_asterisk else STAR_STRONG_RE
        star_single = SMART_STAR_EMPHASIS_RE if enable_all or enable_asterisk else STAR_EMPHASIS_RE
        underline_triple = SMART_UNDERLINE_TRIPLE_RE if enable_all or enable_underscore else UNDERLINE_TRIPLE_RE
        underline_double = SMART_UNDERLINE_STRONG_RE if enable_all or enable_underscore else UNDERLINE_STRONG_RE
        underline_single = SMART_UNDERLINE_EMPHASIS_RE if enable_all or enable_underscore else UNDERLINE_EMPHASIS_RE

        self.md.inlinePatterns["strong_em"] = DoubleTagPattern(star_triple, 'strong,em')
        self.md.inlinePatterns.add("strong_em2", DoubleTagPattern(underline_triple, 'strong,em'), '>strong_em')
        self.md.inlinePatterns['strong'] = SimpleTagPattern(star_double, 'strong')
        self.md.inlinePatterns.add('strong2', SimpleTagPattern(underline_double, 'strong'), '>strong')
        self.md.inlinePatterns["emphasis"] = SimpleTagPattern(star_single, 'em')
        self.md.inlinePatterns["emphasis2"] = SimpleTagPattern(underline_single, 'em')

        if not enable_all and not enable_asterisk:
            self.md.inlinePatterns.add('uneven_star_em', BetterDoubleTagPattern(UNEVEN_STAR321, 'strong,em'), '>strong_em')
            self.md.inlinePatterns.add('uneven_star_em2', BetterDoubleTagPattern(UNEVEN_STAR312, 'em,strong'), '>uneven_star_em')
        if not enable_all and not enable_underscore:
            self.md.inlinePatterns.add('uneven_underscore_em', BetterDoubleTagPattern(UNEVEN_UNDERSCORE321, 'strong,em'), '>strong_em2')
            self.md.inlinePatterns.add('uneven_underscore_em2', BetterDoubleTagPattern(UNEVEN_UNDERSCORE312, 'em,strong'), '>uneven_underscore_em')

    def reset(self):
        """ Wait to make sure smart_strong hasn't overwritten us. """
        if self.load:
            self.load = False
            self.make_better()


def makeExtension(*args, **kwargs):
    return BetterEmExtension(*args, **kwargs)
