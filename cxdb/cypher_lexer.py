# cxdb/cypher_lexer.py

import ply.lex as lex
from cxdb.cypher_exceptions import CypherLexerError

class CypherLexer:
    tokens = [
        'IDENTIFIER', 'STRING', 'NUMBER',
        'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE',
        'COLON', 'COMMA', 'DOT', 'EQUALS'
    ]

    reserved = {
        'MATCH': 'MATCH',
        'WHERE': 'WHERE',
        'RETURN': 'RETURN',
        'CREATE': 'CREATE',
        'DELETE': 'DELETE',
        'AS': 'AS'
    }

    tokens += list(reserved.values())

    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACE = r'\{'
    t_RBRACE = r'\}'
    t_COLON = r':'
    t_COMMA = r','
    t_DOT = r'\.'
    t_EQUALS = r'='

    def t_IDENTIFIER(self, t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        t.type = self.reserved.get(t.value.upper(), 'IDENTIFIER')
        return t

    def t_STRING(self, t):
        r"'[^']*'"
        t.value = t.value[1:-1]  # Remove quotes
        return t

    def t_NUMBER(self, t):
        r'\d+'
        t.value = int(t.value)
        return t

    t_ignore = ' \t\n'

    def t_error(self, t):
        raise CypherLexerError(f"Illegal character '{t.value[0]}'", t.lexpos)

    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)