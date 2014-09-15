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

CRITIC_INSERT = '<span class="critic critic_insert">%s</span>'
CRITIC_DELETE = '<span class="critic critic_delete">%s</span>'
CRITIC_MARK = '<span class="critic critic_mark">%s</span>'
CRITIC_COMMENT = '<span class="critic critic_comment">%s</span>'
CRITIC_SUB = '<span class="critic critic_delete">{~~%s~</span><span class="critic critic_insert">>%s~~}</span>'


class CriticViewPreprocessor(Preprocessor):
    RE_CRITIC = re.compile(
        r'''
            ((?P<open>\{)
                (?:
                    (?P<ins_open>\+{2})(?P<ins_text>.*?)(?P<ins_close>\+{2})
                  | (?P<del_open>\-{2})(?P<del_text>.*?)(?P<del_close>\-{2})
                  | (?P<mark_open>\={2})(?P<mark_text>.*?)(?P<mark_close>\={2})
                  | (?P<comment>(?P<com_open>\>{2})(?P<com_text>.*?)(?P<com_close>\<{2}))
                  | (?P<sub_open>\~{2})(?P<sub_del_text>.*?)(?P<sub_mid>\~\>)(?P<sub_ins_text>.*?)(?P<sub_close>\~{2})
                )
            (?P<close>\})|.)
        ''',
        re.MULTILINE | re.DOTALL | re.VERBOSE
    )

    def __init__(self, md):
        super(CriticViewPreprocessor, self).__init__(md)
        self.is_critic = False

    def critic_view(self, m):
        if m.group('ins_open'):
            self.is_critic = True
            return self.markdown.htmlStash.store(
                CRITIC_INSERT % self._escape(m.group(0)),
                safe=True
            )
        elif m.group('del_open'):
            self.is_critic = True
            return self.markdown.htmlStash.store(
                CRITIC_DELETE % self._escape(m.group(0)),
                safe=True
            )
        elif m.group('mark_open'):
            self.is_critic = True
            return self.markdown.htmlStash.store(
                CRITIC_MARK % self._escape(m.group(0)),
                safe=True
            )
        elif m.group('com_open'):
            self.is_critic = True
            return self.markdown.htmlStash.store(
                CRITIC_COMMENT % self._escape(m.group(0)),
                safe=True
            )
        elif m.group('sub_open'):
            self.is_critic = True
            return self.markdown.htmlStash.store(
                CRITIC_SUB % (
                    self._escape(m.group("sub_del_text")),
                    self._escape(m.group("sub_ins_text"))
                ),
                safe=True
            )
        else:
            return self.markdown.htmlStash.store(
                self._escape(m.group(0)),
                safe=True
            )

    def critic_ignore(self, m):
        if self.config["mode"] == 'accept':
            if m.group('ins_open'):
                return m.group('ins_text')
            elif m.group('del_open'):
                return ''
            elif m.group('mark_open'):
                return m.group('mark_text')
            elif m.group('com_open'):
                return ''
            elif m.group('sub_open'):
                return m.group('sub_ins_text')
            else:
                return m.group(0)
        else:
            if m.group('ins_open'):
                return ''
            elif m.group('del_open'):
                return m.group('del_text')
            elif m.group('mark_open'):
                return m.group('mark_text')
            elif m.group('com_open'):
                return ''
            elif m.group('sub_open'):
                return m.group('sub_del_text')
            else:
                return m.group(0)

    def run(self, lines):
        """ Match and store Fenced Code Blocks in the HtmlStash. """
        text = ''
        processor = self.critic_ignore

        if self.config['mode'] == "ignore":
            processor = self.critic_view

        for m in self.RE_CRITIC.finditer('\n'.join(lines)):
            text += processor(m)
        return text.split('\n') if self.is_critic else lines

    def _escape(self, txt):
        """ basic html escaping """
        txt = txt.replace('&', '&amp;')
        txt = txt.replace('<', '&lt;')
        txt = txt.replace('>', '&gt;')
        txt = txt.replace('"', '&quot;')
        txt = txt.replace("\n", "<br>")
        return txt


class CriticExtension(Extension):
    def __init__(self, *args, **kwargs):
        self.config = {
            'mode': ['ignore', "Critic mode to run in ('ignore', 'accept', or 'reject') - Default: ignore "]
        }

        if "mode" in kwargs and kwargs["mode"] not in ('ignore', 'accept', 'reject'):
            del kwargs["mode"]

        super(CriticExtension, self).__init__(*args, **kwargs)

    def extendMarkdown(self, md, md_globals):
        """ Add FencedBlockPreprocessor to the Markdown instance. """
        critic = CriticViewPreprocessor(md)
        critic.config = self.getConfigs()
        md.preprocessors.add('critic', critic, ">normalize_whitespace")
        md.registerExtension(self)


def makeExtension(*args, **kwargs):
    return CriticExtension(*args, **kwargs)
