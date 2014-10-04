from pygments.lexer import RegexLexer, include, bygroups
from pygments.lexers._mapping import LEXERS
from pygments.token import *

__all__ = ["TrexLexer"]


class TrexLexer(RegexLexer):
    name = 'Trex'
    aliases = ['trex', 'windex', 'sasdex', 'lindex']
    filenames = ['*.trex', '*.trx', '*.def']
    mimetypes = ['text/trex']

    tokens = {
        'root': [
            (r'(?i)\b(?:command|subr|Macro)\b', Keyword.Type, 'function'),
            (r'(?i)\be(?:command|subr|macro)\b', Keyword.Type),
            (r'\b((?i)E?(?:ByteMap|BitMap|Enum|Enumnd))\b', Name.Class),
            (r'\b((?i)(?:stack|darray|barray|tarray|parray|uvar|ustr|ulcl|for|efor|in|break|continue|default|while|ewhile|do|until|return|rreturn|if|else|elseif|eif|case|switch|eswitch|pause|end|define|goto|quit|dosubr))\b', Keyword),
            (r'!|\$|%|&|\*|\-\-|\-|\+\+|\+|~|===|==|=|!=|!==|<=|>=|<<=|>>=|>>>=|<>|<|>|!|&&|\|\||\||\?\:|\*=|(?<!\()/=|%=|\+=|\-=|&amp;=|\^=', Operator),
            (r'\b((0(x|X)[0-9a-fA-F]*)|[0-9-a-fA-F]+h|(([0-9]+\.?[0-9]*)|(\.[0-9]+))((e|E)(\+|-)?[0-9]+)?)(L|l|UL|ul|u|U|F|f)?\b', Number),
            (r'\b((?i)(?:and|or|xor))\b', Operator.Word),
            (r'\b((?i)(?:null|true|false|on|off))\b', Keyword.Constant),
            (r'#\s*((?i)(?:bmentry|(?:un)?define|deprecate(?:off|on)|else(?:if)?|ifn?def|endif|events(?:on|off)|onvclk(?:defer|resume)|smbl(?:info|value)|include|watch(?:on|off)))\b', Keyword.Decleration),
            (r'^[ \t]*(@)([\w\.]+)', bygroups(Keyword.Namespace, String.Other)),
            (r'"', String.Double, 'quoted-string'),
            include('comment'),
            (r' |\t', Whitespace),
            (r'.', Text),
        ],

        'quoted-string': [
            (r'\\.', String.Escape),
            (r'[^"]', String),
            (r'"', String.Double, "#pop")
        ],

        'function': [
            (r'[\w.]+', Name.Function, 'function-variables'),
            include('whitespace'),
            include('comment'),
        ],

        'function-variables': [
            (r'[\w.]+', Name.Variable),
            include('whitespace'),
            include('comment'),
        ],

        'whitespace': [
            (r' |\t', Whitespace),
        ],

        'comment': [
            (r'(?s)/\*.*?\*/', Comment.Multiline),
            (r'//.*\n', Comment.Single),
        ]
    }


# Add to mapping
LEXERS["TrexLexer"] = (
    "pygments.lexers.TrexLexer",
    TrexLexer.name,
    tuple(TrexLexer.aliases),
    tuple(TrexLexer.filenames),
    tuple(TrexLexer.mimetypes)
)
