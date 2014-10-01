"""
pymdown.smartfence
Smart Fenced Code Blocks

This is a modification of the original Fenced Code Extension.
Algorithm has been changed to allow for fenced blocks in blockquotes,
lists, etc.

Fenced Code Extension for Python Markdown
=========================================

This extension adds Fenced Code Blocks to Python-Markdown.

See <https://pythonhosted.org/Markdown/extensions/fenced_code_blocks.html>
for documentation.

Original code Copyright 2007-2008 [Waylan Limberg](http://achinghead.com/).


All changes Copyright 2008-2014 The Python Markdown Project

License: [BSD](http://www.opensource.org/licenses/bsd-license.php)
"""

from __future__ import absolute_import
from __future__ import unicode_literals
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
from markdown.extensions.codehilite import CodeHilite, CodeHiliteExtension, parse_hl_lines
import re

FENCED_START = r'''(?x)
(?P<fence>^(?P<ws>[\> ]*)(?:~{3,}|`{3,}))[ ]*           # Fence opening
(\{?                                                    # Language opening
\.?(?P<lang>[a-zA-Z0-9_+-]*))?[ ]*                      # Language
(hl_lines=(?P<quot>"|')(?P<hl_lines>.*?)(?P=quot))?[ ]* # highlight lines
}?[ ]*$                                                 # Language closing
'''
FENCED_END = r'^%s[ ]*$'
WS = r'^([\> ]{0,%d})(.*)'


class SmartFencedCodeExtension(Extension):

    def extendMarkdown(self, md, md_globals):
        """ Add FencedBlockPreprocessor to the Markdown instance. """
        md.registerExtension(self)
        self.md = md

    def patch_fenced_rule(self):
        fenced = SmartFencedBlockPreprocessor(self.md)
        if 'fenced_code_block' in self.md.preprocessors.keys():
            self.md.preprocessors['fenced_code_block'] = fenced
        else:
            self.md.preprocessors.add(
                'fenced_code_block',
                fenced,
                ">normalize_whitespace"
            )

    def reset(self):
        self.patch_fenced_rule()


class SmartFencedBlockPreprocessor(Preprocessor):
    fence_start = re.compile(FENCED_START)
    CODE_WRAP = '<pre><code%s>%s</code></pre>'
    LANG_TAG = ' class="%s"'

    def __init__(self, md):
        super(SmartFencedBlockPreprocessor, self).__init__(md)

        self.checked_for_codehilite = False
        self.codehilite_conf = {}

    def deindent(self, lines, ws):
        """ Deindent the fenced block lines """
        return '\n'.join([line.replace(self.ws, "", 1) for line in lines]) + '\n'

    def check_codehilite(self):
        """ Check for code hilite extension """
        if not self.checked_for_codehilite:
            for ext in self.markdown.registeredExtensions:
                if isinstance(ext, CodeHiliteExtension):
                    self.codehilite_conf = ext.config
                    break
            self.checked_for_codehilite = True

    def clear(self):
        """ Reset the class variables. """
        self.ws = None
        self.fence = None
        self.lang = None
        self.hl_lines = None
        self.quote_level = 0
        self.code = []
        self.empty_lines = 0
        self.whitespace = None
        self.fence_end = None

    def eval(self, m, start, end):
        """ Evaluate a normal fence """
        if m.group(0).strip() == '':
            # Empty line is okay
            self.empty_lines += 1
            self.code.append('')
        elif len(m.group(1)) != self.ws_len and m.group(2) != '':
            # Not indented enough
            self.clear()
        elif self.fence_end.match(m.group(0)) is not None:
            # End of fence
            self.highlight(self.deindent(self.code, self.ws), start, end)
            self.clear()
        else:
            # Content line
            self.empty_lines = 0
            self.code.append(m.group(0)[len(self.ws):])

    def eval_quoted(self, m, quote_level, start, end):
        """ Evaluate fence inside a blockquote """
        if quote_level > self.quote_level:
            # Quote level exceeds the starting quote level
            self.clear()
        elif quote_level <= self.quote_level:
            if m.group(2) == '':
                # Empty line is okay
                self.code.append('')
                self.empty_lines += 1
            elif len(m.group(1)) < self.ws_len:
                # Not indented enough
                self.clear()
            elif self.empty_lines and quote_level < self.quote_level:
                # Quote levels don't match and we are signified
                # the end of the block with an empty line
                self.clear()
            elif self.fence_end.match(m.group(0)) is not None:
                # End of fence
                self.highlight(self.deindent(self.code, self.ws), start, end)
                self.clear()
            else:
                # Content line
                self.empty_lines = 0
                self.code.append(m.group(2))

    def run(self, lines):
        """ Search for fenced blocks """
        self.check_codehilite()
        self.clear()
        self.stack = []

        count = 0
        for line in lines:
            if self.fence is None:
                # Found the start of a fenced block.
                m = self.fence_start.match(line)
                if m is not None:
                    start = count
                    self.ws = m.group('ws') if m.group('ws') else ''
                    self.ws_len = len(self.ws)
                    self.quote_level = self.ws.count(">")
                    self.empty_lines = 0
                    self.fence = m.group('fence')
                    self.lang = m.group('lang')
                    self.hl_lines = m.group('hl_lines')
                    self.fence_end = re.compile(FENCED_END % self.fence)
                    self.whitespace = re.compile(WS % self.ws_len)
            else:
                # Evaluate lines
                # - Determine if it is the ending line or content line
                # - If is a content line, make sure it is all indentend
                #   with the opening and closing lines (lines with just
                #   whitespace will be stripped so those don't matter).
                # - When content lines are inside blockquotes, make sure
                #   the nested block quote levels make sense according to
                #   blockquote rules.
                m = self.whitespace.match(line)
                if m:
                    end = count + 1
                    quote_level = m.group(1).count(">")

                    if self.quote_level:
                        # Handle blockquotes
                        self.eval_quoted(m, quote_level, start, end)
                    elif quote_level == 0:
                        # Handle all other cases
                        self.eval(m, start, end)
                    else:
                        # Looks like we got a blockquote line
                        # when not in a blockquote.
                        self.clear()
                else:
                    self.clear()
            count += 1

        # Now that we are done iterating the lines,
        # let's replace the original content with the
        # fenced blocks.
        while len(self.stack):
            fenced, start, end = self.stack.pop()
            lines = lines[:start] + [fenced] + lines[end:]
        return lines

    def highlight(self, source, start, end):
        """
        If config is not empty, then the codehighlite extension
        is enabled, so we call it to highlight the code
        """
        if self.codehilite_conf:
            code = CodeHilite(
                source,
                linenums=self.codehilite_conf['linenums'][0],
                guess_lang=self.codehilite_conf['guess_lang'][0],
                css_class=self.codehilite_conf['css_class'][0],
                style=self.codehilite_conf['pygments_style'][0],
                lang=self.lang,
                noclasses=self.codehilite_conf['noclasses'][0],
                hl_lines=parse_hl_lines(self.hl_lines)
            ).hilite()
        else:
            lang = lang = self.LANG_TAG % self.lang if self.lang else ''
            code = self.CODE_WRAP % (lang, self._escape(source))

        placeholder = self.markdown.htmlStash.store(code, safe=True)

        self.stack.append(('%s%s' % (self.ws, placeholder), start, end))

    def _escape(self, txt):
        """ basic html escaping """
        txt = txt.replace('&', '&amp;')
        txt = txt.replace('<', '&lt;')
        txt = txt.replace('>', '&gt;')
        txt = txt.replace('"', '&quot;')
        return txt


def makeExtension(*args, **kwargs):
    return SmartFencedCodeExtension(*args, **kwargs)
