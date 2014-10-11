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
from markdown.postprocessors import Postprocessor
import re

STX = '\u0002'
ETX = '\u0003'
CRITIC_KEY = "czjqqkd:%s"
CRITIC_PLACEHOLDER = "%s" % CRITIC_KEY % r'[0-9]+'
CRITIC_PLACEHOLDER_RE = re.compile(
    r"""(?x)
    (?:
        \<p\>%(stx)s(?P<p_key>%(key)s)%(etx)s\</p\> |
        %(stx)s(?P<key>%(key)s)%(etx)s
    )
    """ % {"key": CRITIC_PLACEHOLDER, "stx": STX, "etx": ETX}
)

RE_CRITIC = re.compile(
    r'''
        ((?P<escapes>\\?)(?P<critic>(?P<open>\{)
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

RE_BLOCK_SEP = re.compile(r'^\n{2,}$')


class CriticStash(object):
    """
    Critic Stash
    """

    def __init__(self):
        self.stash = {}
        self.count = 0

    def __len__(self):
        return len(self.stash)

    def get(self, key, default=None):
        code = self.stash.get(key, default)
        return code

    def remove(self, key):
        del self.stash[key]

    def store(self, code):
        key = CRITIC_KEY % str(self.count)
        self.stash[key] = code
        self.count += 1
        return STX + key + ETX

    def clear_stash(self):
        self.stash = {}
        self.count = 0


class CriticsPostprocessor(Postprocessor):
    def __init__(self, critic_stash):
        super(CriticsPostprocessor, self).__init__()
        self.critic_stash = critic_stash

    def run(self, text):
        """ Replace critic placeholders """

        stack = []

        for m in CRITIC_PLACEHOLDER_RE.finditer(text):
            if m.group('p_key') is not None:
                key = m.group('p_key')
            else:
                key = m.group('key')
            content = self.critic_stash.get(key)
            if content is not None:
                stack.append((m.start(), m.end(), content))
                self.critic_stash.remove(key)

        for item in reversed(stack):
            text = text[:item[0]] + item[2] + text[item[1]:]

        return text


class CriticViewPreprocessor(Preprocessor):
    def __init__(self, critic_stash):
        super(CriticViewPreprocessor, self).__init__()
        self.critic_stash = critic_stash

    def _ins(self, text):
        if RE_BLOCK_SEP.match(text):
            return self.critic_stash.store('<br><ins class="critic break">&nbsp;</ins><br>')
        return (
            self.critic_stash.store('<ins class="critic">') +
            text +
            self.critic_stash.store('</ins>')
        )

    def _del(self, text):
        if RE_BLOCK_SEP.match(text):
            return self.critic_stash.store('<del class="critic break">&nbsp;</del>')
        return (
            self.critic_stash.store('<del class="critic">') +
            text +
            self.critic_stash.store('</del>')
        )

    def _mark(self, text):
        return (
            self.critic_stash.store('<mark class="critic">') +
            text +
            self.critic_stash.store('</mark>')
        )

    def _comment(self, text):
        return (
            self.critic_stash.store(
                '<span class="critic comment">' +
                self._escape(text, strip_nl=True) +
                '</span>'
            )
        )

    def critic_view(self, m):
        if m.group('escapes'):
            return m.group('critic')
        if m.group('ins_open'):
            return self._ins(m.group('ins_text'))
        elif m.group('del_open'):
            return self._del(m.group('del_text'))
        elif m.group('sub_open'):
            return (
                self._del(m.group('sub_del_text')) +
                self._ins(m.group('sub_ins_text'))
            )
        elif m.group('mark_open'):
            return self._mark(m.group('mark_text'))
        elif m.group('com_open'):
            return self._comment(m.group('com_text'))
        else:
            return m.group(0)

    def critic_parse(self, m):
        accept = self.config["mode"] == 'accept'
        if m.group('escapes'):
            return m.group('critic')
        if m.group('ins_open'):
            return m.group('ins_text') if accept else ''
        elif m.group('del_open'):
            return '' if accept else m.group('del_text')
        elif m.group('mark_open'):
            return m.group('mark_text')
        elif m.group('com_open'):
            return ''
        elif m.group('sub_open'):
            return m.group('sub_ins_text') if accept else ('sub_del_text')
        else:
            return m.group(0)

    def _escape(self, txt, strip_nl=False):
        """ basic html escaping """
        txt = txt.replace('&', '&amp;')
        txt = txt.replace('<', '&lt;')
        txt = txt.replace('>', '&gt;')
        txt = txt.replace('"', '&quot;')
        txt = txt.replace("\n", "<br>" if not strip_nl else ' ')
        return txt

    def run(self, lines):
        """ Match and store Fenced Code Blocks in the HtmlStash. """
        text = ''
        processor = self.critic_parse
        view_mode = self.config['mode'] == "view"

        if view_mode:
            processor = self.critic_view

        for m in RE_CRITIC.finditer('\n'.join(lines)):
            text += processor(m)

        return text.split('\n')


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
        self.critic_stash = CriticStash()
        post = CriticsPostprocessor(self.critic_stash)
        critic = CriticViewPreprocessor(self.critic_stash)
        critic.config = self.getConfigs()
        self.md.preprocessors.add('critic', critic, ">normalize_whitespace")
        self.md.postprocessors.add("critic-post", post, ">raw_html")

    def reset(self):
        """
        Wait to until after all extensions have been loaded
        so we can be as sure as we can that this is the first
        thing run after "normalize_whitespace"
        """

        if not self.configured:
            self.configured = True
            self.insert_critic()
        else:
            self.critic_stash.clear()


def makeExtension(*args, **kwargs):
    return CriticExtension(*args, **kwargs)
