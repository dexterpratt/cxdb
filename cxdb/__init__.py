"""
CXDB: A lightweight, in-memory graph database that supports basic Cypher operations.

This package provides the core functionality for creating, managing, and querying
graph databases using a subset of the Cypher query language.
"""

from .core import CXDB
from .ndex import NDExConnector
from .cypher_parser import CypherParser
from .cypher_lexer import CypherLexer
from .query_executor import CypherQueryExecutor
from .cypher_exceptions import CypherSyntaxError, CypherSemanticError, CypherLexerError

__all__ = [
    'CXDB',
    'NDExConnector',
    'CypherParser',
    'CypherLexer',
    'CypherQueryExecutor',
    'CypherSyntaxError',
    'CypherSemanticError',
    'CypherLexerError',
]

__version__ = "0.1.1"