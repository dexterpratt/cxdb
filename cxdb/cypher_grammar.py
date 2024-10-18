"""
Cypher Grammar Module

This module defines the grammar rules for parsing Cypher queries.
It is used by the CypherParser class to construct the Abstract Syntax Tree (AST).
"""

from cxdb.cypher_ast import (
    Query, MatchClause, CreateClause, DeleteClause, WhereClause,
    ReturnClause, OrderByClause, LimitClause, PatternPath, NodePattern,
    RelationshipPattern, Expression, LogicalExpression, Condition,
    ReturnItem, FunctionCall, OrderItem
)
from cxdb.cypher_lexer import CypherLexer
from cxdb.cypher_exceptions import CypherSyntaxError

class CypherGrammar:
    tokens = CypherLexer.tokens
    start = 'query'

    precedence = (
        ('left', 'OR'),
        ('left', 'AND'),
        ('left', 'PLUS'),
    )

    def p_query(self, p):
        """query : clauses"""
        p[0] = Query(p[1])

    def p_clauses(self, p):
        """clauses : clause
                   | clause clauses"""
        p[0] = [p[1]] if len(p) == 2 else [p[1]] + p[2]

    def p_clause(self, p):
        """clause : match_clause
                  | create_clause
                  | delete_clause
                  | return_clause
                  | order_by_clause
                  | limit_clause"""
        p[0] = p[1]

    def p_match_clause(self, p):
        """match_clause : MATCH pattern_path where_clause"""
        p[0] = MatchClause(p[2], p[3])

    def p_pattern_path(self, p):
        """pattern_path : pattern"""
        p[0] = PatternPath(p[1])

    def p_pattern(self, p):
        """pattern : node_pattern
                   | node_pattern relationship_chain"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]] + p[2]

    def p_relationship_chain(self, p):
        """relationship_chain : relationship_pattern node_pattern
                              | relationship_pattern node_pattern relationship_chain"""
        if len(p) == 3:
            p[0] = [p[1], p[2]]
        else:
            p[0] = [p[1], p[2]] + p[3]

    def p_node_pattern(self, p):
        """node_pattern : LPAREN IDENTIFIER COLON IDENTIFIER properties RPAREN
                        | LPAREN IDENTIFIER COLON IDENTIFIER RPAREN
                        | LPAREN COLON IDENTIFIER properties RPAREN
                        | LPAREN COLON IDENTIFIER RPAREN"""
        if len(p) == 7:
            p[0] = NodePattern(p[2], p[4], p[5])
        elif len(p) == 6 and p[2] == ':':
            p[0] = NodePattern(None, p[3], p[4])
        elif len(p) == 6:
            p[0] = NodePattern(p[2], p[4], None)
        else:
            p[0] = NodePattern(None, p[3], None)

    def p_relationship_pattern(self, p):
        """relationship_pattern : DASH LBRACKET relationship_detail RBRACKET ARROW
                                | DASH LBRACKET relationship_detail RBRACKET DASH
                                | DASH ARROW
                                | DASH"""
        if len(p) == 6:
            direction = True if p[5] == '->' else None
            p[0] = p[3]
            p[0].direction = direction
        else:
            direction = True if len(p) == 3 else None
            p[0] = RelationshipPattern(None, None, None, None, direction)

    def p_relationship_detail(self, p):
        """relationship_detail : IDENTIFIER COLON IDENTIFIER properties
                               | COLON IDENTIFIER properties
                               | IDENTIFIER COLON IDENTIFIER
                               | COLON IDENTIFIER
                               | properties
                               | empty"""
        if len(p) == 5:
            p[0] = RelationshipPattern(p[1], p[3], p[4], None, None)
        elif len(p) == 4 and p[1] == ':':
            p[0] = RelationshipPattern(None, p[2], p[3], None, None)
        elif len(p) == 4:
            p[0] = RelationshipPattern(p[1], p[3], None, None, None)
        elif len(p) == 3:
            p[0] = RelationshipPattern(None, p[2], None, None, None)
        elif len(p) == 2:
            p[0] = RelationshipPattern(None, None, p[1], None, None)
        else:
            p[0] = RelationshipPattern(None, None, None, None, None)

    def p_properties(self, p):
        """properties : LBRACE property_list RBRACE"""
        p[0] = dict(p[2])

    def p_property_list(self, p):
        """property_list : property
                         | property COMMA property_list"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]] + p[3]

    def p_property(self, p):
        """property : IDENTIFIER COLON value"""
        p[0] = (p[1], p[3])

    def p_create_clause(self, p):
        """create_clause : CREATE pattern"""
        p[0] = CreateClause(p[2])

    def p_delete_clause(self, p):
        """delete_clause : DELETE expression_list
                         | DETACH DELETE expression_list"""
        if len(p) == 3:
            p[0] = DeleteClause(p[2], False)
        else:
            p[0] = DeleteClause(p[3], True)

    def p_expression_list(self, p):
        """expression_list : expression
                           | expression COMMA expression_list"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]] + p[3]

    def p_expression(self, p):
        """expression : IDENTIFIER
                    | IDENTIFIER DOT IDENTIFIER
                    | function_call
                    | STRING
                    | NUMBER
                    | expression PLUS expression
                    | expression CONTAINS expression
                    | expression ENDS_WITH expression"""
        if len(p) == 2:
            p[0] = Expression(p[1])
        elif len(p) == 4:
            if p[2] == '.':
                p[0] = Expression(f"{p[1]}.{p[3]}")
            elif p[2] in ('PLUS', 'CONTAINS', 'ENDS_WITH'):
                p[0] = Expression((p[2], p[1], p[3]))
            else:
                p[0] = Expression((p[2], p[1], p[3]))
        else:
            p[0] = p[1]

    def p_where_clause(self, p):
        """where_clause : WHERE boolean_expr
                        | empty"""
        p[0] = WhereClause(p[2]) if p[1] == 'WHERE' else None

    def p_boolean_expr(self, p):
        """boolean_expr : condition
                        | boolean_expr AND boolean_expr
                        | boolean_expr OR boolean_expr
                        | LPAREN boolean_expr RPAREN"""
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 4:
            if p[1] == '(':
                p[0] = p[2]
            else:
                p[0] = LogicalExpression(p[1], p[2], p[3])

    def p_condition(self, p):
        """condition : expression comparison_operator expression
                     | expression IS NULL
                     | expression IS NOT NULL"""
        if len(p) == 4:
            if p[2] == 'IS':
                p[0] = Condition(p[1], 'IS NULL', None)
            else:
                p[0] = Condition(p[1], p[2], p[3])
        else:
            p[0] = Condition(p[1], 'IS NOT NULL', None)

    def p_comparison_operator(self, p):
        """comparison_operator : EQUALS
                               | GT
                               | LT
                               | GE
                               | LE
                               | NE
                               | STARTS_WITH"""
        p[0] = p[1]

    def p_return_clause(self, p):
        """return_clause : RETURN return_items
                         | RETURN DISTINCT return_items"""
        if len(p) == 3:
            p[0] = ReturnClause(p[2], False)
        else:
            p[0] = ReturnClause(p[3], True)

    def p_return_items(self, p):
        """return_items : return_item
                        | return_item COMMA return_items"""
        p[0] = [p[1]] if len(p) == 2 else [p[1]] + p[3]

    def p_return_item(self, p):
        """return_item : expression
                       | expression AS IDENTIFIER"""
        if len(p) == 2:
            p[0] = ReturnItem(p[1], None)
        else:
            p[0] = ReturnItem(p[1], p[3])

    def p_function_call(self, p):
        """function_call : IDENTIFIER LPAREN function_args RPAREN"""
        p[0] = FunctionCall(p[1], p[3])

    def p_function_args(self, p):
        """function_args : expression
                         | expression COMMA function_args
                         | empty"""
        if len(p) == 2:
            p[0] = [p[1]] if p[1] is not None else []
        else:
            p[0] = [p[1]] + p[3]

    def p_order_by_clause(self, p):
        """order_by_clause : ORDER BY order_items"""
        p[0] = OrderByClause(p[3])

    def p_order_items(self, p):
        """order_items : order_item
                       | order_item COMMA order_items"""
        p[0] = [p[1]] if len(p) == 2 else [p[1]] + p[3]

    def p_order_item(self, p):
        """order_item : expression
                      | expression ASC
                      | expression DESC"""
        if len(p) == 2:
            p[0] = OrderItem(p[1], 'ASC')
        else:
            p[0] = OrderItem(p[1], p[2])

    def p_limit_clause(self, p):
        """limit_clause : LIMIT NUMBER"""
        p[0] = LimitClause(p[2])

    def p_value(self, p):
        """value : STRING
                 | NUMBER"""
        p[0] = p[1]

    def p_empty(self, p):
        """empty :"""
        pass

    def p_error(self, p):
        if p:
            raise CypherSyntaxError(f"Syntax error at '{p.value}'", p.lineno, p.lexpos, p.type)
        else:
            raise CypherSyntaxError("Incomplete query")
