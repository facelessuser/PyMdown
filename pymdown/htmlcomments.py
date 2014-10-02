"""
pymdown.htmlcomments
An extension for Python Markdown.
Strip classes, styles, and ids from html

MIT license.

Copyright (c) 2014 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from __future__ import unicode_literals
from markdown import Extension
from markdown.postprocessors import Postprocessor
import re

RE_HTML_COMMENTS = re.compile(r'<!--[\s\S]*?-->')


class HtmlCommentsPostprocessor(Postprocessor):
    def run(self, text):
        """ Strip comments """

        return RE_HTML_COMMENTS.sub('', text)


class HtmlCommentsExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        """ Add HtmlCommentsPostprocessor """

        htmlcomments = HtmlCommentsPostprocessor(md)
        md.postprocessors.add("html-comments", htmlcomments, "_end")
        md.registerExtension(self)


def makeExtension(*args, **kwargs):
    return HtmlCommentsExtension(*args, **kwargs)
