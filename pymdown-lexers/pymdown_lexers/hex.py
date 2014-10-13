from pygments.lexer import RegexLexer, include, bygroups
from pygments.token import *

__all__ = ["HexLexer"]


class HexLexer(RegexLexer):
    name = 'Hex'
    aliases = ['hex']
    filenames = ['*.hex']
    mimetypes = ['text/hex']

    tokens = {
        'root': [
            (r'^([a-f\d]{8}\:)([ \t]*)', bygroups(String, Whitespace), 'address'),
            (r'^(\s*)(::.*?)$', bygroups(Whitespace, Comment.Single)),
            (r'^.+?$', Error),  # invalid
            (r'.+?$', Comment.Single)
        ],

        'address': [
            (r'([ \t]*)(?:(\:)|$)', bygroups(Whitespace, String), '#pop'),
            (r'[\da-f]{1}', Number, 'byte'),
            (r'[ \t]', Whitespace),
            (r'.+$', Error, '#pop')  # invalid
        ],

        'byte': [
            (r'[\da-f]{1}', Text, '#pop'),
            (r'.', Error, '#pop')  # invalid
        ]
    }
