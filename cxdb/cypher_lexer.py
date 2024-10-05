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
        'LPAREN', 'RPAREN', 'COLON', 'COMMA', 'DOT', 'EQUALS',
        'GT', 'LT', 'GE', 'LE', 'NE'
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

    # Simple tokens
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_COLON = r':'
    t_COMMA = r','
    t_DOT = r'\.'
    t_EQUALS = r'='
    t_GT = r'>'
    t_LT = r'<'
    t_GE = r'>='
    t_LE = r'<='
    t_NE = r'<>'

    def t_IDENTIFIER(self, t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        """
        Rule for identifiers and reserved keywords.

        Matches alphanumeric strings starting with a letter or underscore.
        Checks if the matched string is a reserved keyword.

        Args:
            t (ply.lex.LexToken): The token object.

        Returns:
            ply.lex.LexToken: The processed token.
        """
        t.type = self.reserved.get(t.value.upper(), 'IDENTIFIER')
        return t

    def t_STRING(self, t):
        r"'[^']*'"
        """
        Rule for string literals.

        Matches strings enclosed in single quotes.
        Removes the enclosing quotes from the token value.

        Args:
            t (ply.lex.LexToken): The token object.

        Returns:
            ply.lex.LexToken: The processed token.
        """
        t.value = t.value[1:-1]  # Remove quotes
        return t

    def t_NUMBER(self, t):
        r'\d+'
        """
        Rule for numeric literals.

        Matches one or more digits and converts the value to an integer.

        Args:
            t (ply.lex.LexToken): The token object.

        Returns:
            ply.lex.LexToken: The processed token.
        """
        t.value = int(t.value)
        return t

    # Ignored characters (spaces and tabs)
    t_ignore = ' \t\n'

    def t_error(self, t):
        """
        Error handling function for illegal characters.

        Args:
            t (ply.lex.LexToken): The token object where the error occurred.

        Raises:
            CypherLexerError: If an illegal character is encountered.
        """
        raise CypherLexerError(f"Illegal character '{t.value[0]}'", t.lexpos)

    def build(self, **kwargs):
        """
        Build the lexer.

        This method creates the PLY lexer object based on the defined rules.

        Args:
            **kwargs: Additional keyword arguments to pass to ply.lex.lex().
        """
        self.lexer = lex.lex(module=self, **kwargs)