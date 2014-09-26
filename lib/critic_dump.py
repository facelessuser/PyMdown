#!/usr/bin/env python
"""
pymdown.critic_dump

Strips and returns the the markdown with critic marks removed

Licensed under MIT
Copyright (c) 2014 Isaac Muse <isaacmuse@gmail.com>
"""
import re

CRITIC_IGNORE = 0
CRITIC_ACCEPT = 1
CRITIC_REJECT = 2
CRITIC_VIEW = 4
CRITIC_DUMP = 8
CRITIC_OFF = 16

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

class CriticDump(object):

    def process(self, m):
        if self.accept:
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

    def dump(self, source, accept):
        """ Match and store Fenced Code Blocks in the HtmlStash. """
        text = ''
        self.accept = accept
        for m in RE_CRITIC.finditer(source):
            text += self.process(m)

        return text
