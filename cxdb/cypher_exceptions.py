# cxdb/cypher_exceptions.py

class CypherParserError(Exception):
    """Base class for exceptions in the Cypher parser."""
    pass

class CypherLexerError(CypherParserError):
    """Exception raised for errors in the lexical analysis."""
    def __init__(self, message, position):
        self.message = message
        self.position = position
        super().__init__(f"{message} at position {position}")

class CypherSyntaxError(CypherParserError):
    """Exception raised for syntax errors."""
    def __init__(self, message, line=None, column=None, token=None):
        self.message = message
        self.line = line
        self.column = column
        self.token = token
        error_message = message
        if line is not None and column is not None:
            error_message += f" at line {line}, column {column}"
        if token is not None:
            error_message += f" (token: {token})"
        super().__init__(error_message)

class CypherSemanticError(CypherParserError):
    """Exception raised for semantic errors."""
    def __init__(self, message):
        self.message = message
        super().__init__(message)