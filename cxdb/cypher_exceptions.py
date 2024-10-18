"""
Cypher Exceptions Module

This module defines custom exceptions for the Cypher query language implementation.
"""

class CypherError(Exception):
    """Base class for Cypher-related exceptions."""
    pass

class CypherSyntaxError(CypherError):
    """Exception raised for syntax errors in Cypher queries."""
    def __init__(self, message, lineno=None, column=None, token_type=None):
        self.message = message
        self.lineno = lineno
        self.column = column
        self.token_type = token_type
        super().__init__(self.message)

class CypherSemanticError(CypherError):
    """Exception raised for semantic errors in Cypher queries."""
    pass

class CypherLexerError(CypherError):
    """Exception raised for lexer errors in Cypher queries."""
    def __init__(self, message, lineno=None, column=None):
        self.message = message
        self.lineno = lineno
        self.column = column
        super().__init__(self.message)
