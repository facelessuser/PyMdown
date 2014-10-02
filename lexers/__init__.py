from pygments.lexers._mapping import LEXERS

def add_lexers():
    LEXERS['TrexLexer'] = ('lexers.trex', "Trex", ('trex',), ('*.trex', '*.trx', '*.def'), ('text/trex'))
