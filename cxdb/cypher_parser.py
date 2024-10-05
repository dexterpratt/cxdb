"""
Cypher Parser Module

This module provides a parser for the Cypher query language used in CXDB.
It defines the grammar rules for parsing Cypher queries and constructs
an Abstract Syntax Tree (AST) representation of the parsed query.

The module uses the PLY (Python Lex-Yacc) library for lexical analysis
and parsing. It works in conjunction with the CypherLexer to tokenize
and parse Cypher queries.

Classes:
    CypherParser: The main parser class for Cypher queries.
    Various AST node classes (MatchClause, CreateClause, etc.): Represent
    different components of a Cypher query in the AST.
"""

import ply.yacc as yacc
from cxdb.cypher_lexer import CypherLexer
from cxdb.cypher_exceptions import CypherSyntaxError, CypherSemanticError

class CypherParser:
    """
    A parser for Cypher queries.

    This class defines the grammar rules for parsing Cypher queries and
    constructs an Abstract Syntax Tree (AST) representation of the parsed query.

    Attributes:
        tokens (list): A list of token names, inherited from CypherLexer.
        start (str): The starting symbol for the grammar.
        lexer (CypherLexer): An instance of the Cypher lexer.
        parser (ply.yacc.LRParser): The PLY parser object.
    """

    tokens = CypherLexer.tokens
    start = 'query'

    def __init__(self):
        """
        Initialize the CypherParser.

        Creates instances of CypherLexer and PLY parser.
        """
        self.lexer = CypherLexer()
        self.lexer.build()
        self.parser = yacc.yacc(module=self, debug=False, write_tables=False)

    def parse(self, data):
        """
        Parse a Cypher query string.

        Args:
            data (str): The Cypher query string to parse.

        Returns:
            The root node of the Abstract Syntax Tree representing the parsed query.
        """
        return self.parser.parse(data, lexer=self.lexer.lexer)

    def p_query(self, p):
        """query : match_clause
                 | create_clause
                 | delete_clause"""
        p[0] = p[1]

    def p_match_clause(self, p):
        """match_clause : MATCH node_pattern where_clause return_clause
                        | MATCH node_pattern where_clause RETURN"""
        if len(p) == 5 and p[4] == 'RETURN':
            raise CypherSyntaxError("Incomplete RETURN clause")
        p[0] = MatchClause(p[2], p[3], p[4] if len(p) > 4 else None)

    def p_create_clause(self, p):
        """create_clause : CREATE node_pattern"""
        p[0] = CreateClause(p[2])

    def p_delete_clause(self, p):
        """delete_clause : DELETE node_pattern where_clause"""
        p[0] = DeleteClause(p[2], p[3])

    def p_node_pattern(self, p):
        """node_pattern : LPAREN IDENTIFIER COLON IDENTIFIER RPAREN"""
        p[0] = NodePattern(p[2], p[4])

    def p_where_clause(self, p):
        """where_clause : WHERE condition
                        | empty"""
        p[0] = p[1] if len(p) == 3 else None

    def p_condition(self, p):
        """condition : IDENTIFIER DOT IDENTIFIER comparison_operator value"""
        p[0] = Condition(p[1], p[3], p[4], p[5])

    def p_comparison_operator(self, p):
        """comparison_operator : EQUALS
                               | GT
                               | LT
                               | GE
                               | LE
                               | NE"""
        p[0] = p[1]

    def p_return_clause(self, p):
        """return_clause : RETURN return_items"""
        p[0] = ReturnClause(p[2])

    def p_return_items(self, p):
        """return_items : return_item
                        | return_item COMMA return_items"""
        p[0] = [p[1]] if len(p) == 2 else [p[1]] + p[3]

    def p_return_item(self, p):
        """return_item : IDENTIFIER
                       | IDENTIFIER DOT IDENTIFIER
                       | IDENTIFIER DOT IDENTIFIER AS IDENTIFIER"""
        if len(p) == 2:
            p[0] = ReturnItem(p[1], p[1])
        elif len(p) == 4:
            p[0] = ReturnItem(f"{p[1]}.{p[3]}", f"{p[1]}.{p[3]}")
        else:  # AS
            p[0] = ReturnItem(f"{p[1]}.{p[3]}", p[5])

    def p_value(self, p):
        """value : STRING
                 | NUMBER"""
        p[0] = p[1]

    def p_empty(self, p):
        """empty :"""
        pass

    def p_error(self, p):
        if p:
            if p.type == 'RETURN':
                # Check if there's any non-whitespace after RETURN
                remaining = p.lexer.lexdata[p.lexpos + len(p.value):].strip()
                if not remaining:
                    raise CypherSyntaxError("Incomplete RETURN clause")
            raise CypherSyntaxError(f"Syntax error at '{p.value}'", p.lineno, p.lexpos, p.type)
        else:
            raise CypherSyntaxError("Incomplete query")
        
# AST node classes
class MatchClause:
    """
    Represents a MATCH clause in a Cypher query.

    Attributes:
        pattern (NodePattern): The node pattern to match.
        where (Condition): The WHERE condition, if any.
        return_ (ReturnClause): The RETURN clause.
    """
    def __init__(self, pattern, where, return_):
        self.pattern = pattern
        self.where = where
        self.return_ = return_

class CreateClause:
    """
    Represents a CREATE clause in a Cypher query.

    Attributes:
        node_pattern (NodePattern): The node pattern to create.
    """
    def __init__(self, node_pattern):
        self.node_pattern = node_pattern

class DeleteClause:
    """
    Represents a DELETE clause in a Cypher query.

    Attributes:
        node_pattern (NodePattern): The node pattern to delete.
        where (Condition): The WHERE condition, if any.
    """
    def __init__(self, node_pattern, where):
        self.node_pattern = node_pattern
        self.where = where

class NodePattern:
    """
    Represents a node pattern in a Cypher query.

    Attributes:
        identifier (str): The identifier of the node.
        label (str): The label of the node.
    """
    def __init__(self, identifier, label):
        self.identifier = identifier
        self.label = label

class Condition:
    """
    Represents a condition in a WHERE clause.

    Attributes:
        identifier (str): The identifier of the node.
        property (str): The property of the node to compare.
        operator (str): The comparison operator.
        value (str): The value to compare against.
    """
    def __init__(self, identifier, property_, operator, value):
        self.identifier = identifier
        self.property = property_
        self.operator = operator
        self.value = value

class ReturnClause:
    """
    Represents a RETURN clause in a Cypher query.

    Attributes:
        items (list): A list of ReturnItem objects.
    """
    def __init__(self, items):
        self.items = items

class ReturnItem:
    """
    Represents a single item in a RETURN clause.

    Attributes:
        expression (str): The expression to return.
        alias (str): The alias for the returned expression, if any.
    """
    def __init__(self, expression, alias):
        self.expression = expression
        self.alias = alias

    def __repr__(self):
        return f"ReturnItem(expression='{self.expression}', alias='{self.alias}')"