# cypher_exceptions.py

class CypherParserError(Exception):
    """Base class for exceptions in the Cypher parser."""
    pass

class CypherLexerError(CypherParserError):
    """Exception raised for errors in the lexical analysis."""
    def __init__(self, message, position):
        self.message = message
        self.position = position

class CypherSyntaxError(CypherParserError):
    """Exception raised for syntax errors."""
    def __init__(self, message, line, column, token):
        self.message = message
        self.line = line
        self.column = column
        self.token = token

class CypherSemanticError(CypherParserError):
    """Exception raised for semantic errors."""
    pass