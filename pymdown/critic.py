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

CRITIC_DELETE = '<del class="critic">%s</del>'
CRITIC_INSERT = '<ins class="critic">%s</ins>'
CRITIC_MARK = '<mark class="critic">%s</mark>'
CRITIC_COMMENT = '<span class="critic">%s</span>'

CRITIC_DELETE_P = '<del class="critic break">&nbsp;</del>'
CRITIC_INSERT_P = '\n\n<ins class="critic break">&nbsp;</ins>\n\n'
CRITIC_MARK_P = '<br><br>'
CRITIC_COMMENT_P = ' '


class CriticViewPreprocessor(Preprocessor):
    RE_CRITIC = re.compile(
        r'''
            ((?P<escapes>\\*)(?P<critic>(?P<open>\{)
                (?:
                    (?P<ins_open>\+{2})(?P<ins_text>.*?)(?P<ins_close>\+{2})
                  | (?P<del_open>\-{2})(?P<del_text>.*?)(?P<del_close>\-{2})
                  | (?P<mark_open>\={2})(?P<mark_text>.*?)(?P<mark_close>\={2})
                  | (?P<comment>(?P<com_open>\>{2})(?P<com_text>.*?)(?P<com_close>\<{2}))
                  | (?P<sub_open>\~{2})(?P<sub_del_text>.*?)(?P<sub_mid>\~\>)(?P<sub_ins_text>.*?)(?P<sub_close>\~{2})
                )
            (?P<close>\}))|.)
        ''',
        re.MULTILINE | re.DOTALL | re.VERBOSE
    )
    nl2br = False

    def _edits(self, text, replace, br, changes=False, strip_nl=False):
        parts = text.split('\n')
        queue = ''
        text = ''
        last_break = False
        for part in parts:
            if part == '':
                if changes:
                    if queue:
                        # Convert previous text first
                        text += replace % self._escape(queue)
                        queue = ''

                    if not last_break:
                        # No previous new lines
                        text += br
                        last_break = True

                elif not last_break:
                    queue += br
                    last_break = True

            else:
                if queue and not last_break:
                    part = '\n' + part
                queue += part if changes else self._escape(part, strip_nl)
                last_break = False

        if queue:
            text += replace % (self._escape(queue, strip_nl) if changes else queue)
            queue = ''
        return text

    def _ins(self, text, escapes=''):
        if self.raw:
            return CRITIC_INSERT % self._escape(text)
        else:
            return escapes + self._edits(text, CRITIC_INSERT, CRITIC_INSERT_P, changes=True)

    def _del(self, text, escapes):
        if self.raw:
            return CRITIC_DELETE % self._escape(text)
        else:
            return escapes + self._edits(text, CRITIC_DELETE, CRITIC_DELETE_P, changes=True)

    def _mark(self, text, escapes):
        if self.raw:
            return CRITIC_MARK % self._escape(text)
        else:
            return escapes + self._edits(text, CRITIC_MARK, CRITIC_MARK_P)

    def _comment(self, text, escapes):
        if self.raw:
            return CRITIC_COMMENT % self._escape(text, strip_nl=True)
        else:
            return escapes + self._edits(text, CRITIC_COMMENT, CRITIC_COMMENT_P, strip_nl=True)

    def critic_view(self, m):
        escapes = m.group('escapes')
        if escapes and len(escapes) % 2:
            escaped = "%s%s" % (escapes[:-1], m.group('critic'))
            return self._escape(escaped) if self.raw else escaped
        if escapes is None:
            escapes = ''
        if m.group('ins_open'):
            return self._ins(m.group('ins_text'), escapes)
        elif m.group('del_open'):
            return self._del(m.group('del_text'), escapes)
        elif m.group('mark_open'):
            return self._mark(m.group('mark_text'), escapes)
        elif m.group('com_open'):
            return self._comment(m.group('com_text'), escapes)
        elif m.group('sub_open'):
            return (
                self._del(m.group('sub_del_text'), escapes) +
                self._ins(m.group('sub_ins_text'))
            )
        else:
            return self._escape(m.group(0)) if self.raw else m.group(0)

    def critic_parse(self, m):
        accept = self.config["mode"] == 'accept'
        escapes = m.group('escapes')
        if escapes and len(escapes) % 2:
            return "%s%s" % (escapes[:-1], m.group('critic'))
        if escapes is None:
            escapes = ''
        if m.group('ins_open'):
            return '%s%s' % (escapes, m.group('ins_text') if accept else '')
        elif m.group('del_open'):
            return '%s%s' % (escapes, '' if accept else m.group('del_text'))
        elif m.group('mark_open'):
            return '%s%s' % (escapes, m.group('mark_text'))
        elif m.group('com_open'):
            return escapes
        elif m.group('sub_open'):
            return '%s%s' % (escapes, m.group('sub_ins_text') if accept else ('sub_del_text'))
        else:
            return m.group(0)

    def run(self, lines):
        """ Match and store Fenced Code Blocks in the HtmlStash. """
        text = ''
        processor = self.critic_parse
        view_mode = self.config['mode'] == "view"

        if view_mode:
            processor = self.critic_view

        self.raw = bool(self.config['raw_view']) and view_mode

        for m in self.RE_CRITIC.finditer('\n'.join(lines)):
            text += processor(m)
        if self.raw:
            text = '<pre class="critic-pre">%s</pre>' % text
        return text.split('\n')

    def _escape(self, txt, strip_nl=False):
        """ basic html escaping """
        txt = txt.replace('&', '&amp;')
        txt = txt.replace('<', '&lt;')
        txt = txt.replace('>', '&gt;')
        txt = txt.replace('"', '&quot;')
        txt = txt.replace("\n", "<br>" if (self.nl2br or self.raw) and not strip_nl else ' ')
        return txt


class CriticExtension(Extension):
    def __init__(self, *args, **kwargs):
        self.config = {
            'mode': ['view', "Critic mode to run in ('view', 'accept', or 'reject') - Default: view "],
            'raw_view': [False, "Raw view keeps the output as the raw markup for view mode - Default False"]
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
        critic = CriticViewPreprocessor(self.md)
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
