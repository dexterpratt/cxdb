"""
Cypher Parser Module

This module provides a parser for the Cypher query language used in CXDB.
It integrates the grammar rules and semantic analysis to parse Cypher queries
and construct an Abstract Syntax Tree (AST) representation of the parsed query.

The module uses the PLY (Python Lex-Yacc) library for lexical analysis
and parsing. It works in conjunction with the CypherLexer, CypherGrammar,
and CypherSemanticAnalyzer to tokenize, parse, and analyze Cypher queries.

Classes:
    CypherParser: The main parser class for Cypher queries.
"""

import ply.yacc as yacc
from cxdb.cypher_lexer import CypherLexer
from cxdb.cypher_grammar import CypherGrammar
from cxdb.cypher_semantic_analyzer import CypherSemanticAnalyzer
from cxdb.cypher_exceptions import CypherSyntaxError, CypherSemanticError
from cxdb.cypher_ast import *

class CypherParser:
    def __init__(self):
        self.lexer = CypherLexer()
        self.lexer.build()
        self.grammar = CypherGrammar()
        self.semantic_analyzer = CypherSemanticAnalyzer()
        self.parser = yacc.yacc(module=self.grammar, debug=False, write_tables=False)

    def parse(self, data):
        try:
            # Tokenize the input
            self.lexer.input(data)
            # Parse the tokens
            ast = self.parser.parse(lexer=self.lexer)
            # Perform semantic analysis
            self.semantic_analyzer.check_semantics(ast)
            return ast
        except CypherSyntaxError as e:
            # Raise syntax errors
            raise CypherSyntaxError(f"Syntax Error: {str(e)}")
        except CypherSemanticError as e:
            # Raise semantic errors
            raise CypherSemanticError(f"Semantic Error: {str(e)}")

# Export CypherParser and all AST classes
__all__ = ['CypherParser', 'Query', 'MatchClause', 'CreateClause', 'DeleteClause',
           'PatternPath', 'NodePattern', 'RelationshipPattern', 'WhereClause',
           'ReturnClause', 'OrderByClause', 'LimitClause', 'Expression',
           'FunctionCall', 'LogicalExpression', 'Condition']
