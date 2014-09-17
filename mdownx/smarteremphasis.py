"""
mdownx.smarteremphasis
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

SMART_STAR_EMPHASIS_RE = r'(?<![a-zA-Z\d*])(\*)(?![\*\s])(.+?\**?)(?<!\s)\2(?![a-zA-Z\d*])'
SMART_STAR_STRONG_RE = r'(?<![a-zA-Z\d*])(\*{2})(?![\*\s])(.+?\**?)(?<!\s)\2(?![a-zA-Z\d*])'
SMART_STAR_TRIPLE_RE = r'(?<![a-zA-Z\d*])(\*{3})(?![\*\s])(.+?\**?)(?<!\s)\2(?![a-zA-Z\d*])'
SMART_UNDERLINE_EMPHASIS_RE = r'(?<![a-zA-Z\d_])(_)(?![_\s])(.+?_*?)(?<!\s)\2(?![a-zA-Z\d_])'
SMART_UNDERLINE_STRONG_RE = r'(?<![a-zA-Z\d_])(_{2})(?![_\s])(.+?_*?)(?<!\s)\2(?![a-zA-Z\d_])'
SMART_UNDERLINE_TRIPLE_RE = r'(?<![a-zA-Z\d_])(_{3})(?![_\s])(.+?_*?)(?<!\s)\2(?![a-zA-Z\d_])'

DUMB_STAR_EMPHASIS_RE = r'(\*)(?!\s)(.*?)(?<!\s)\2'
DUMB_STAR_STRONG_RE = r'(\*{2})(?!\s)(.*?)(?<!\s)\2'
DUMB_STAR_TRIPLE_RE = r'(\*{3})(?!\s)(.*?)(?<!\s)\2'
DUMB_UNDERLINE_EMPHASIS_RE = r'(_)(?!\s)(.*?)(?<!\s)\2'
DUMB_UNDERLINE_STRONG_RE = r'(_{2})(?!\s)(.*?)(?<!\s)\2'
DUMB_UNDERLINE_TRIPLE_RE = r'(_{3})(?!\s)(.*?)(?<!\s)\2'

smart_enable_keys = [
    "all", "asterisk", "underscore", "none"
]


class SmarterEmphasisExtension(Extension):
    """ Add extension to Markdown class."""

    def __init__(self, *args, **kwargs):
        self.config = {
            'smart_enable': ["all", "Treat connected words intelligently - Default: all"]
        }

        if "smart_enable" in kwargs and kwargs["smart_enable"] not in smart_enable_keys:
            del kwargs["smart_enable"]

        super(SmarterEmphasisExtension, self).__init__(*args, **kwargs)

    def extendMarkdown(self, md, md_globals):
        """ Modify inline patterns. """

        self.md = md
        md.registerExtension(self)

    def make_smarter(self):
        """
        This should work with the default smart_strong package enabled or disabled.
        """

        config = self.getConfigs()
        enabled = config["smart_enable"]
        enable_all = enabled == "all"
        enable_underscore = enabled == "underscore"
        enable_asterisk = enabled == "asterisk"

        star_triple = SMART_STAR_TRIPLE_RE if enable_all or enable_asterisk else DUMB_STAR_TRIPLE_RE
        star_double = SMART_STAR_STRONG_RE if enable_all or enable_asterisk else DUMB_STAR_STRONG_RE
        star_single = SMART_STAR_EMPHASIS_RE if enable_all or enable_asterisk else DUMB_STAR_EMPHASIS_RE
        underline_triple = SMART_UNDERLINE_TRIPLE_RE if enable_all or enable_underscore else DUMB_UNDERLINE_TRIPLE_RE
        underline_double = SMART_UNDERLINE_STRONG_RE if enable_all or enable_underscore else DUMB_UNDERLINE_STRONG_RE
        underline_single = SMART_UNDERLINE_EMPHASIS_RE if enable_all or enable_underscore else DUMB_UNDERLINE_EMPHASIS_RE

        self.md.inlinePatterns["strong_em"] = DoubleTagPattern(star_triple, 'strong,em')
        self.md.inlinePatterns.add("strong_em2", DoubleTagPattern(underline_triple, 'strong,em'), '>strong_em')
        self.md.inlinePatterns['strong'] = SimpleTagPattern(star_double, 'strong')
        self.md.inlinePatterns.add('strong2', SimpleTagPattern(underline_double, 'strong'), '>strong')
        self.md.inlinePatterns["emphasis"] = SimpleTagPattern(star_single, 'em')
        self.md.inlinePatterns["emphasis2"] = SimpleTagPattern(underline_single, 'em')

    def reset(self):
        """ Wait to make sure smart_strong hasn't overwritten us."""
        self.make_smarter()


def makeExtension(*args, **kwargs):
    return SmarterEmphasisExtension(*args, **kwargs)
