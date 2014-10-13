from pygments.lexer import RegexLexer, include, bygroups
from pygments.token import *

__all__ = ["CriticMarkupLexer"]


class CriticMarkupLexer(RegexLexer):
    name = 'Critic Markup'
    aliases = ['critic-markup']
    filenames = ['*.critic-markup']
    mimetypes = ['text/critic-markup']

    tokens = {
        'root': [
            (r'(?s)\\\{(?:\+{2}.*?\+{2}|\-{2}.*?\-{2}|={2}.*?={2}|~{2}.*?~>.*?~{2}|>{2}.*?<{2})\}', Text),
            (r'(?s)\{\+{2}.*?\+{2}\}', String),
            (r'(?s)\{\-{2}.*?\-{2}\}', String),
            (r'(?s)\{={2}.*?={2}\}', String),
            (r'(?s)\{>{2}.*?<{2}\}', String),
            (r'(?s)\{~{2}.*?~>.*?~{2}\}', String),
            (r' |\t', Whitespace),
            (r'.', Text)
        ]
    }
