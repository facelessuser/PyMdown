"""
pymdown.critic
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

CRITIC_P = '\n\n'
CRITIC_INSERT = '<ins class="critic">%s</ins>'
CRITIC_DELETE = '<del class="critic">%s</del>'
CRITIC_DELETE_P = '<del class="critic break">&nbsp;</del>'
CRITIC_INSERT_P = '\n\n<ins class="critic break">&nbsp;</ins>\n\n'
CRITIC_MARK = '<mark class="critic">%s</mark>'
CRITIC_COMMENT = '<span class="critic">%s</span>'


class CriticViewPreprocessor(Preprocessor):
    RE_CRITIC = re.compile(
        r'''
            ((?P<escapes>\\*)(?P<open>\{)
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
    nl2br = False

    def _replace(self, text, replace, br):
        parts = text.split('\n')
        queue = ''
        text = ''
        last_break = False
        for part in parts:
            if part == '':
                if queue:
                    # Convert previous text first
                    text += replace % self._escape(queue)
                    queue = ''
                    last_break = False

                if not last_break:
                    # No previous new lines
                    text += br
                    last_break = True
            else:
                if queue:
                    queue += '\n'
                queue += part
        if queue:
            text += replace % self._escape(queue)
            queue = ''
        return text

    def _ins(self, text):
        return self._replace(text, CRITIC_INSERT, CRITIC_INSERT_P)

    def _del(self, text):
        return self._replace(text, CRITIC_DELETE, CRITIC_DELETE_P)

    def _mark(self, text):
        return self._replace(text, CRITIC_MARK, CRITIC_P)

    def _comment(self, text):
        return self._replace(text, CRITIC_COMMENT, CRITIC_P)

    def critic_view(self, m):
        if m.group('escapes') and len(m.group('escapes')) % 2:
            return m.group(0)
        elif m.group('ins_open'):
            return self._ins(m.group('ins_text'))
        elif m.group('del_open'):
            return self._del(m.group('del_text'))
        elif m.group('mark_open'):
            return self._mark(m.group('mark_text'))
        elif m.group('com_open'):
            return self._comment(m.group('com_text'))
        elif m.group('sub_open'):
            return (
                self._del(m.group('sub_del_text')) +
                self._ins(m.group('sub_ins_text'))
            )
        else:
            return m.group(0)

    def critic_ignore(self, m):
        accept = self.config["mode"] == 'accept'
        if m.group('escapes') and len(m.group('escapes')) % 2:
            return m.group(0)
        elif m.group('ins_open'):
            return m.group('ins_text') if accept else ''
        elif m.group('del_open'):
            return '' if accept else m.group('del_text')
        elif m.group('mark_open'):
            return m.group('mark_text')
        elif m.group('com_open'):
            return '' if accept else ''
        elif m.group('sub_open'):
            return m.group('sub_ins_text') if accept else ('sub_del_text')
        else:
            return m.group(0)

    def run(self, lines):
        """ Match and store Fenced Code Blocks in the HtmlStash. """
        text = ''
        processor = self.critic_ignore

        if self.config['mode'] == "view":
            processor = self.critic_view

        for m in self.RE_CRITIC.finditer('\n'.join(lines)):
            text += processor(m)
        return text.split('\n')

    def _escape(self, txt):
        """ basic html escaping """
        txt = txt.replace('&', '&amp;')
        txt = txt.replace('<', '&lt;')
        txt = txt.replace('>', '&gt;')
        txt = txt.replace('"', '&quot;')
        txt = txt.replace("\n", "<br>" if self.nl2br else ' ')
        return txt


class CriticExtension(Extension):
    def __init__(self, *args, **kwargs):
        self.config = {
            'mode': ['view', "Critic mode to run in ('view', 'accept', or 'reject') - Default: view "]
        }

        if "mode" in kwargs and kwargs["mode"] not in ('view', 'accept', 'reject'):
            del kwargs["mode"]

        super(CriticExtension, self).__init__(*args, **kwargs)

        self.configured = False

    def extendMarkdown(self, md, md_globals):
        """ Add FencedBlockPreprocessor to the Markdown instance. """
        self.md = md
        md.registerExtension(self)

    def insert_critic(self):
        critic = CriticViewPreprocessor()
        critic.config = self.getConfigs()
        self.md.preprocessors.add('critic', critic, "_begin")

    def reset(self):
        """
        Wait to until after all extensions have been loaded
        so we can be as sure as we can that this is the first
        thing run after "normalize_whitespace"
        """

        if not self.configured:
            self.configured = True
            self.insert_critic()


def makeExtension(*args, **kwargs):
    return CriticExtension(*args, **kwargs)
