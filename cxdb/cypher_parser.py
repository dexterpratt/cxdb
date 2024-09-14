# cxdb/cypher_parser.py

import ply.yacc as yacc
from cxdb.cypher_lexer import CypherLexer
from cxdb.cypher_exceptions import CypherSyntaxError, CypherSemanticError

class CypherParser:
    tokens = [
        'IDENTIFIER', 'STRING', 'NUMBER',
        'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE',
        'COLON', 'COMMA', 'DOT', 'EQUALS', 'AS'
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

    def __init__(self):
        self.lexer = CypherLexer()
        self.lexer.build()
        self.parser = yacc.yacc(module=self, debug=False, write_tables=False)

    def parse(self, data):
        return self.parser.parse(data, lexer=self.lexer.lexer)

    def p_match_clause(self, p):
        '''match_clause : MATCH node_pattern where_clause return_clause'''
        p[0] = MatchClause(p[2], p[3], p[4])

    def p_node_pattern(self, p):
        '''node_pattern : LPAREN IDENTIFIER COLON IDENTIFIER RPAREN'''
        p[0] = NodePattern(p[2], p[4])

    def p_where_clause(self, p):
        '''where_clause : WHERE condition
                        | empty'''
        p[0] = p[1] if len(p) == 3 else None

    def p_condition(self, p):
        '''condition : IDENTIFIER DOT IDENTIFIER EQUALS value'''
        p[0] = Condition(p[1], p[3], p[5])

    def p_return_clause(self, p):
        '''return_clause : RETURN return_items'''
        p[0] = ReturnClause(p[2])

    def p_return_items(self, p):
        '''return_items : return_item
                        | return_item COMMA return_items'''
        p[0] = [p[1]] if len(p) == 2 else [p[1]] + p[3]

    def p_return_item(self, p):
        '''return_item : IDENTIFIER
                       | IDENTIFIER DOT IDENTIFIER
                       | IDENTIFIER DOT IDENTIFIER AS IDENTIFIER'''
        if len(p) == 2:
            p[0] = ReturnItem(p[1], p[1])
        elif len(p) == 4:
            p[0] = ReturnItem(f"{p[1]}.{p[3]}", f"{p[1]}.{p[3]}")
        else:  # AS
            p[0] = ReturnItem(f"{p[1]}.{p[3]}", p[5])

    def p_value(self, p):
        '''value : STRING
                 | NUMBER'''
        p[0] = p[1]

    def p_empty(self, p):
        'empty :'
        pass

    def p_error(self, p):
        if p:
            raise CypherSyntaxError(f"Syntax error at '{p.value}'", p.lineno, p.lexpos, p.type)
        else:
            raise CypherSyntaxError("Syntax error at EOF")
        
    def p_query(self, p):
        '''query : match_clause
                 | create_clause
                 | delete_clause'''
        p[0] = p[1]

    def p_create_clause(self, p):
        '''create_clause : CREATE node_pattern'''
        p[0] = CreateClause(p[2])

    def p_delete_clause(self, p):
        '''delete_clause : DELETE node_pattern where_clause'''
        p[0] = DeleteClause(p[2], p[3])

# AST node classes
class MatchClause:
    def __init__(self, match, where, return_):
        self.match = match
        self.where = where
        self.return_ = return_

class CreateClause:
    def __init__(self, node_pattern):
        self.node_pattern = node_pattern

class DeleteClause:
    def __init__(self, node_pattern, where):
        self.node_pattern = node_pattern
        self.where = where

class NodePattern:
    def __init__(self, identifier, label):
        self.identifier = identifier
        self.label = label

class Condition:
    def __init__(self, identifier, property_, value):
        self.identifier = identifier
        self.property = property_
        self.value = value

class ReturnClause:
    def __init__(self, items):
        self.items = items

class ReturnItem:
    def __init__(self, expression, alias):
        self.expression = expression
        self.alias = alias

    def __repr__(self):
        return f"ReturnItem(expression='{self.expression}', alias='{self.alias}')"