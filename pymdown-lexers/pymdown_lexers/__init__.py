from pygments.lexers._mapping import LEXERS
from .trex import TrexLexer

__all__ = ["TrexLexer"]

# Add lexers to mapping
for lexer in __all__:
    lexer_obj = globals()[lexer]
    LEXERS[lexer_obj.__name__] = (
        "pygments.lexers.%s" % lexer_obj.module,
        lexer_obj.name,
        tuple(lexer_obj.aliases),
        tuple(lexer_obj.filenames),
        tuple(lexer_obj.mimetypes)
    )
