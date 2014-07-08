"""
mdownx.plainhtml
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


# Strip out id, class and style attributes for a simple html output
# Since we are stripping out two attributes, we need to set up the groups in such
# a way so we can retrieve the data we don't want to throw away
# up to these worst case scenarios:
#
# <tag attr=""... (id|class|style)=""... attr=""... (id|class|style)=""... attr=""... (id|class|style)=""...>
# <tag (id|class|style)=""... attr=""... (id|class|style)=""... attr=""... (id|class|style)=""... attr=""...>
RE_STRIP_HTML = re.compile(
    r'''
        (?P<open><[\w\:\.\-]+)                                                            # Tag open
        (?:
            (?P<attr1>(?:\s+(?!id|class|style)[\w\-:]+(?:\s*=\s*(?:"[^"]*"|'[^']*'))?)*)  # Attributes to keep
          | (?P<target1>\s+(?:id|class|style)(?:\s*=\s*(?:"[^"]*"|'[^']*'))*)             # Attributes to delte
        )
        (?:
            (?P<attr2>(?:\s+(?!id|class|style)[\w\-:]+(?:\s*=\s*(?:"[^"]*"|'[^']*'))?)*)  # Attributes to keep
          | (?P<target2>\s+(?:id|class|style)(?:\s*=\s*(?:"[^"]*"|'[^']*'))*)             # Attributes to delte
        )?
        (?:
            (?P<attr3>(?:\s+(?!id|class|style)[\w\-:]+(?:\s*=\s*(?:"[^"]*"|'[^']*'))?)*)  # Attributes to keep
          | (?P<target3>\s+(?:id|class|style)(?:\s*=\s*(?:"[^"]*"|'[^']*'))*)             # Attributes to delte
        )?
        (?:
            (?P<attr4>(?:\s+(?!id|class|style)[\w\-:]+(?:\s*=\s*(?:"[^"]*"|'[^']*'))?)*)  # Attributes to keep
          | (?P<target4>\s+(?:id|class|style)(?:\s*=\s*(?:"[^"]*"|'[^']*'))*)             # Attributes to delte
        )?
        (?:
            (?P<attr5>(?:\s+(?!id|class|style)[\w\-:]+(?:\s*=\s*(?:"[^"]*"|'[^']*'))?)*)  # Attributes to keep
          | (?P<target5>\s+(?:id|class|style)(?:\s*=\s*(?:"[^"]*"|'[^']*'))*)             # Attributes to delte
        )?
        (?:
            (?P<attr6>(?:\s+(?!id|class|style)[\w\-:]+(?:\s*=\s*(?:"[^"]*"|'[^']*'))?)*)  # Attributes to keep
          | (?P<target6>\s+(?:id|class|style)(?:\s*=\s*(?:"[^"]*"|'[^']*'))*)             # Attributes to delte
        )?
        (?P<close>\s*(?:\/?)>)                                                            # Tag end
    ''',
    re.MULTILINE | re.DOTALL | re.VERBOSE
)


def repl(m):
    tag = m.group('open')
    if m.group('attr1'):
        tag += m.group('attr1')
    if m.group('attr2'):
        tag += m.group('attr2')
    if m.group('attr3'):
        tag += m.group('attr3')
    if m.group('attr4'):
        tag += m.group('attr4')
    if m.group('attr5'):
        tag += m.group('attr5')
    if m.group('attr6'):
        tag += m.group('attr6')
    tag += m.group('close')
    return tag


class PlainHtmlPostprocessor(Postprocessor):
    def run(self, text):
        ''' Strip out ids and classes for a simplified HTML output '''

        return RE_STRIP_HTML.sub(repl, text)


class PlainHtmlExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        """Add HeaderAnchorTreeprocessor to Markdown instance"""

        plainhtml = PlainHtmlPostprocessor(md)
        md.postprocessors.add("plainhtml", plainhtml, "_end")
        md.registerExtension(self)


def makeExtension(configs={}):
    return PlainHtmlExtension(configs=configs)
