import re
import codecs
from .logger import Logger
import traceback

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


class MdownCriticDumpException(Exception):
    pass


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

    def dump(self, source, encoding, accept):
        """ Match and store Fenced Code Blocks in the HtmlStash. """
        text = ''
        try:
            with codecs.open(source, "r", encoding=encoding) as f:
                self.accept = accept
                for m in RE_CRITIC.finditer(f.read()):
                    text += self.process(m)
        except:
            Logger.log(str(traceback.format_exc()))
            raise MdownCriticDumpException("Critic parsing failed!")

        return text
