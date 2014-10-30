from __future__ import absolute_import
from __future__ import unicode_literals
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
import re

FLOW = 0
SEQUENCE = 1

uml_map = {
    FLOW: 'flow',
    SEQUENCE: 'sequence'
}


class UmlCodeExtension(Extension):
    def __init__(self, *args, **kwargs):
        self.configured = False
        super(UmlCodeExtension, self).__init__(*args, **kwargs)

    def extendMarkdown(self, md, md_globals):
        """ Add FencedBlockPreprocessor to the Markdown instance. """
        self.md = md
        md.registerExtension(self)

    def insert_uml(self):
        nestedfences = False
        for ext in self.md.registeredExtensions:
            if ext.__class__.__name__ == 'NestedFencesCodeExtension':
                nestedfences = True
                break
        if not nestedfences:
            if 'fenced_code_block' in self.md.preprocessors.keys():
                insert_pt = '<fenced_code_block'
            else:
                insert_pt = ">normalize_whitespace"
            self.md.preprocessors.add(
                'uml_code_block',
                UmlBlockPreprocessor(self.md),
                insert_pt
            )

    def reset(self):
        if not self.configured:
            self.insert_uml()
            self.configured = True


class UmlFormatter(object):
    CODE_WRAP = '<pre class="uml-%s"><code>%s</code></pre>'
    CLASS_ATTR = ' class="%s"'

    def __init__(self, src=None, uml_type=None):
        self.src = src
        self.uml_type = uml_map.get(uml_type, None)

    def format(self):
        return self.CODE_WRAP % (self.uml_type, self._escape(self.src))

    def _escape(self, txt):
        """ basic html escaping """
        txt = txt.replace('&', '&amp;')
        txt = txt.replace('<', '&lt;')
        txt = txt.replace('>', '&gt;')
        txt = txt.replace('"', '&quot;')
        return txt


class UmlBlockPreprocessor(Preprocessor):
    UML_BLOCK_RE = re.compile(
        r'''(?xsm)
        (?P<fence>^(?:~{3,}|`{3,}))[ ]*                    # Opening
        (\{?\.?(?P<uml>(?:flow|sequence)))?[ ]*\}?[ ]*\n   # Optional {, and uml type
        (?P<code>.*?)(?<=\n)                               # Content
        (?P=fence)[ ]*$                                    # Closing
        '''
    )

    def run(self, lines):
        """ Match and store Fenced Code Blocks in the HtmlStash. """

        text = "\n".join(lines)
        while 1:
            m = self.UML_BLOCK_RE.search(text)
            if m:
                uml_type = None
                if m.group('uml'):
                    for k, v in uml_map.items():
                        if v == m.group('uml'):
                            uml_type = k

                if uml_type is not None:
                    code = UmlFormatter(m.group('code'), uml_type).format()
                    placeholder = self.markdown.htmlStash.store(code, safe=True)
                    text = '%s\n%s\n%s' % (text[:m.start()], placeholder, text[m.end():])
            else:
                break
        return text.split("\n")


def makeExtension(*args, **kwargs):
    return UmlCodeExtension(*args, **kwargs)
