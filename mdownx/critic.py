"""
mdownx.critic
Parses critic markup and outputs the file in a more visual HTML.
Must be the last extension loaded.

MIT license.

Copyright (c) 2014 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from __future__ import absolute_import
from __future__ import unicode_literals
from markdown import Extension
from markdown.preprocessors import Preprocessor
import re


class CriticViewPreprocessor(Preprocessor):
    RE_CRITIC = re.compile(
        r'''
            ((?P<open>\{)
                (?:
                    (?P<ins_open>\+{2})(?P<ins_text>.*?)(?P<ins_close>\+{2})
                  | (?P<del_open>\-{2})(?P<del_text>.*?)(?P<del_close>\-{2})
                  | (?P<mark_open>\={2})(?P<mark_text>.*?)(?P<mark_close>\={2})
                  | (?P<com_open>\>{2})(?P<com_text>.*?)(?P<com_close>\<{2})
                  | (?P<sub_open>\~{2})(?P<sub_del_text>.*?)(?P<sub_mid>\~\>)(?P<sub_ins_text>.*?)(?P<sub_close>\~{2})
                )
            (?P<close>\})|.)
        ''',
        re.MULTILINE | re.DOTALL | re.VERBOSE
    )
    def __init__(self, md):
        super(CriticViewPreprocessor, self).__init__(md)

    def insert(self, m):
        return self.markdown.htmlStash.store("<ins>%s</ins>" % self._escape(m.group('ins_text')), safe=True)

    def delete(self, m):
        return self.markdown.htmlStash.store("<del>%s</del>" % self._escape(m.group('del_text')), safe=True)

    def mark(self, m):
        return self.markdown.htmlStash.store("<mark>%s</mark>" % self._escape(m.group('mark_text')), safe=True)

    def comment(self, m):
        return self.markdown.htmlStash.store("<span class=\"critic_comment\">%s</span>" % self._escape(m.group("com_text")), safe=True)

    def substitute(self, m):
        return self.markdown.htmlStash.store("<ins>%s</ins><del>%s</del>" % (self._escape(m.group("sub_del_text")), self._escape(m.group("sub_ins_text"))), safe=True)

    def critic_hit(self, m):
        if m.group('ins_open'):
            return self.insert(m)
        elif m.group('del_open'):
            return self.delete(m)
        elif m.group('mark_open'):
            return self.mark(m)
        elif m.group('com_open'):
            return self.comment(m)
        elif m.group('sub_open'):
            return self.substitute(m)
        else:
            return self.markdown.htmlStash.store(self._escape(m.group(0)), safe=True)

    def run(self, lines):
        """ Match and store Fenced Code Blocks in the HtmlStash. """
        text = ''
        for m in self.RE_CRITIC.finditer('\n'.join(lines)):
            text += self.critic_hit(m)
        return text.split('\n')

    def _escape(self, txt):
        """ basic html escaping """
        txt = txt.replace('&', '&amp;')
        txt = txt.replace('<', '&lt;')
        txt = txt.replace('>', '&gt;')
        txt = txt.replace('"', '&quot;')
        txt = txt.replace("\n", "<br>")
        return txt


class CriticExtension(Extension):

    def extendMarkdown(self, md, md_globals):
        """ Add FencedBlockPreprocessor to the Markdown instance. """
        md.registerExtension(self)

        md.preprocessors.add('critic', CriticViewPreprocessor(md), ">normalize_whitespace")


def makeExtension(configs=None):
    return CriticExtension(configs=configs)
