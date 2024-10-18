"""
Cypher Lexer Module

This module provides a lexer for the Cypher query language used in CXDB.
It defines the tokens and lexical rules for tokenizing Cypher queries.

The module uses the PLY (Python Lex-Yacc) library for lexical analysis.
It works in conjunction with the CypherParser to tokenize and parse Cypher queries.

Classes:
    CypherLexer: The main lexer class for Cypher queries.
"""

import ply.lex as lex
from cxdb.cypher_exceptions import CypherLexerError

class CypherLexer:
    """
    A lexer for Cypher queries.

    This class defines the tokens and lexical rules for tokenizing Cypher queries.
    It uses the PLY library to generate a lexer based on the defined rules.

    Attributes:
        tokens (list): A list of token names recognized by the lexer.
        reserved (dict): A dictionary of reserved keywords in Cypher.
        lexer (ply.lex.Lexer): The PLY lexer object.
    """

    tokens = [
        'IDENTIFIER', 'STRING', 'NUMBER',
        'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'LBRACKET', 'RBRACKET',
        'COLON', 'COMMA', 'DOT', 'EQUALS', 'DASH', 'ARROW',
        'GT', 'LT', 'GE', 'LE', 'NE',
        'STARTS_WITH', 'PLUS', 'CONTAINS', 'ENDS_WITH'
    ]

    t_CONTAINS = r'CONTAINS'
    t_ENDS_WITH = r'ENDS\s+WITH'

    reserved = {
        'MATCH': 'MATCH',
        'WHERE': 'WHERE',
        'RETURN': 'RETURN',
        'CREATE': 'CREATE',
        'DELETE': 'DELETE',
        'DETACH': 'DETACH',
        'AS': 'AS',
        'ORDER': 'ORDER',
        'BY': 'BY',
        'LIMIT': 'LIMIT',
        'DISTINCT': 'DISTINCT',
        'AND': 'AND',
        'OR': 'OR',
        'IS': 'IS',
        'NULL': 'NULL',
        'NOT': 'NOT',
        'ASC': 'ASC',
        'DESC': 'DESC',
        'STARTS': 'STARTS',
        'WITH': 'WITH'
    }

    tokens += list(reserved.values())

    # Simple tokens
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACE = r'\{'
    t_RBRACE = r'\}'
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'
    t_COLON = r':'
    t_COMMA = r','
    t_DOT = r'\.'
    t_EQUALS = r'='
    t_DASH = r'-'
    t_ARROW = r'->'
    t_GT = r'>'
    t_LT = r'<'
    t_GE = r'>='
    t_LE = r'<='
    t_NE = r'<>'
    t_PLUS = r'\+'

    def t_STARTS_WITH(self, t):
        r'STARTS\s+WITH'
        return t

    def t_IDENTIFIER(self, t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        t.type = self.reserved.get(t.value.upper(), 'IDENTIFIER')
        return t

    def t_STRING(self, t):
        r"'[^']*'"
        t.value = t.value[1:-1]  # Remove quotes
        return t

    def t_NUMBER(self, t):
        r'\d+(\.\d+)?'
        t.value = float(t.value) if '.' in t.value else int(t.value)
        return t

    # Ignored characters (spaces and tabs)
    t_ignore = ' \t'

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_error(self, t):
        raise CypherLexerError(f"Illegal character '{t.value[0]}'", t.lexer.lineno, t.lexpos)

    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    def input(self, data):
        self.lexer.input(data)

    def token(self):
        return self.lexer.token()
