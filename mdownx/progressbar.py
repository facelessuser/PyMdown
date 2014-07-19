"""
mdownx.progressbar
Really simple plugin to add support for
progress bars

[==30%  MyLabel]

[==50/200 MyLabel]

New line is required before the progress bar.  Can take percentages and divisions.
Floats are okay.  Numbers must be positive.  This is an experimental extension.
Functionality is subject to change.

MIT license.

Copyright (c) 2014 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
from __future__ import unicode_literals
from markdown import Extension
from markdown.inlinepatterns import Pattern, dequote
from markdown import util

RE_PROGRESS = r'\[==\s*(?:(100(?:.0+)?|[1-9]?[0-9](?:.\d+)?)%|(?:(\d+(?:.\d+)?)\s*/\s*(\d+(?:.\d+)?)))(\s+(?:[^\]\\]|\\.)*)?\s*\]'

CLASS_100PLUS = "progress-100plus"
CLASS_80PLUS = "progress-80plus"
CLASS_60PLUS = "progress-60plus"
CLASS_40PLUS = "progress-40plus"
CLASS_20PLUS = "progress-20plus"
CLASS_0PLUS = "progress-0plus"


class ProgressBarPattern(Pattern):
    def __init__(self, pattern):
        Pattern.__init__(self, pattern)

    def create_tag(self, progress_class, width, label):
        el = util.etree.Element("div")
        el.set('class', 'progress')
        bar = util.etree.SubElement(el, 'div')
        bar.set('class', 'progress-bar %s' % progress_class)
        bar.set('style', 'width:%s%%' % width)
        p = util.etree.SubElement(bar, 'p')
        p.set('class', 'progress-label')
        p.text = self.markdown.htmlStash.store(label, safe=True)
        return el

    def handleMatch(self, m):
        label = ""
        if m.group(5):
            label = dequote(m.group(5).strip())
        if m.group(2):
            value = float(m.group(2))
        else:
            try:
                num = float(m.group(3))
            except:
                num = 0.0
            try:
                den = float(m.group(4))
            except:
                den = 1.0
            if den == 0.0:
                den = 1.0

            value = (num / den) * 100.0

            if value > 100.0:
                value = 100.0
            elif value < 0.0:
                value = 0.0

        if value >= 100.0:
            c = CLASS_100PLUS
        elif value >= 80.0:
            c = CLASS_80PLUS
        elif value >= 60.0:
            c = CLASS_60PLUS
        elif value >= 40.0:
            c = CLASS_40PLUS
        elif value >= 20.0:
            c = CLASS_20PLUS
        else:
            c = CLASS_0PLUS

        return self.create_tag(c, '%.2f' % value, label)


class ProgressBarExtension(Extension):
    """Adds progressbar extension to Markdown class."""

    def extendMarkdown(self, md, md_globals):
        """Add for progress bar"""
        progress = ProgressBarPattern(RE_PROGRESS)
        progress.markdown = md
        md.inlinePatterns.add("progressbar", progress, "<reference")


def makeExtension(configs={}):
    return ProgressBarExtension(configs=dict(configs))
