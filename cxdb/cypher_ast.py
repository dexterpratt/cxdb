"""
Cypher Abstract Syntax Tree (AST) Module

This module defines the AST node classes used to represent the structure
of Cypher queries after parsing. These classes are used by the CypherParser
to construct the AST and by the CypherQueryExecutor to execute queries.

Classes:
    Query, MatchClause, CreateClause, DeleteClause, PatternPath, NodePattern,
    RelationshipPattern, WhereClause, ReturnClause, OrderByClause, LimitClause,
    Expression, FunctionCall, LogicalExpression, Condition, ReturnItem, OrderItem
"""

from cxdb.cypher_exceptions import CypherSemanticError

class Query:
    def __init__(self, clauses):
        self.clauses = clauses

    def check_semantics(self, analyzer):
        for clause in self.clauses:
            clause.check_semantics(analyzer)

class MatchClause:
    def __init__(self, pattern_path, where):
        self.pattern_path = pattern_path
        self.where = where

    def check_semantics(self, analyzer):
        self.pattern_path.check_semantics(analyzer)
        if self.where:
            self.where.check_semantics(analyzer)

class CreateClause:
    def __init__(self, pattern):
        self.pattern = pattern

    def check_semantics(self, analyzer):
        for item in self.pattern:
            item.check_semantics(analyzer)

class DeleteClause:
    def __init__(self, expressions, detach):
        self.expressions = expressions
        self.detach = detach

    def check_semantics(self, analyzer):
        for expr in self.expressions:
            expr.check_semantics(analyzer)

class PatternPath:
    def __init__(self, elements):
        self.elements = elements  # List of NodePattern and RelationshipPattern objects

    def check_semantics(self, analyzer):
        for element in self.elements:
            element.check_semantics(analyzer)

class NodePattern:
    def __init__(self, identifier, label, properties):
        self.identifier = identifier
        self.label = label
        self.properties = properties or {}

    def check_semantics(self, analyzer):
        if self.identifier:
            analyzer.add_symbol(self.identifier, 'NODE')

class RelationshipPattern:
    def __init__(self, identifier, label, properties, length, direction):
        self.identifier = identifier
        self.label = label
        self.properties = properties or {}
        self.length = length
        self.direction = direction

    def check_semantics(self, analyzer):
        if self.identifier:
            analyzer.add_symbol(self.identifier, 'RELATIONSHIP')

class WhereClause:
    def __init__(self, boolean_expr):
        self.boolean_expr = boolean_expr

    def check_semantics(self, analyzer):
        self.boolean_expr.check_semantics(analyzer)

class ReturnClause:
    def __init__(self, items, distinct):
        self.items = items
        self.distinct = distinct

    def check_semantics(self, analyzer):
        for item in self.items:
            item.check_semantics(analyzer)

class OrderByClause:
    def __init__(self, items):
        self.items = items

    def check_semantics(self, analyzer):
        for item in self.items:
            item.check_semantics(analyzer)

class LimitClause:
    def __init__(self, limit):
        self.limit = limit

    def check_semantics(self, analyzer):
        if not isinstance(self.limit, int):
            raise CypherSemanticError(f"LIMIT must be an integer, got {type(self.limit)}")

class Expression:
    def __init__(self, value):
        self.value = value

    def check_semantics(self, analyzer):
        if isinstance(self.value, str):
            if analyzer.is_property_access(self.value):
                entity, prop = self.value.split('.', 1)
                if not analyzer.symbol_exists(entity):
                    raise CypherSemanticError(f"Undefined identifier '{entity}'")
            elif not analyzer.is_string_literal(self.value):
                if not analyzer.symbol_exists(self.value):
                    raise CypherSemanticError(f"Undefined identifier '{self.value}'")
        elif isinstance(self.value, (int, float, bool)):
            # These are literals, no need to check
            pass
        elif isinstance(self.value, tuple):
            # Handle operators like CONTAINS and ENDS WITH
            operator, left, right = self.value
            if operator in ('CONTAINS', 'ENDS_WITH'):
                left.check_semantics(analyzer)
                right.check_semantics(analyzer)
        elif hasattr(self.value, 'check_semantics'):
            self.value.check_semantics(analyzer)

class FunctionCall:
    def __init__(self, function_name, arguments):
        self.function_name = function_name
        self.arguments = arguments

    def check_semantics(self, analyzer):
        analyzer.check_function_call(self)
        for arg in self.arguments:
            arg.check_semantics(analyzer)

class LogicalExpression:
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def check_semantics(self, analyzer):
        self.left.check_semantics(analyzer)
        self.right.check_semantics(analyzer)
        analyzer.check_type_match(self)

class Condition:
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def check_semantics(self, analyzer):
        self.left.check_semantics(analyzer)
        if hasattr(self.right, 'check_semantics'):
            self.right.check_semantics(analyzer)
        analyzer.check_condition(self)

class ReturnItem:
    def __init__(self, expression, alias):
        self.expression = expression
        self.alias = alias

    def check_semantics(self, analyzer):
        if isinstance(self.expression, str):
            if '.' in self.expression:
                entity, prop = self.expression.split('.', 1)
                if not analyzer.symbol_exists(entity):
                    raise CypherSemanticError(f"Undefined identifier '{entity}'")
            elif not analyzer.symbol_exists(self.expression):
                raise CypherSemanticError(f"Undefined identifier '{self.expression}'")
        elif hasattr(self.expression, 'check_semantics'):
            self.expression.check_semantics(analyzer)
        if self.alias:
            analyzer.add_symbol(self.alias, 'ALIAS')

class OrderItem:
    def __init__(self, expression, order='ASC'):
        self.expression = expression
        self.order = order

    def check_semantics(self, analyzer):
        if hasattr(self.expression, 'check_semantics'):
            self.expression.check_semantics(analyzer)

# Export all classes
__all__ = [
    'Query', 'MatchClause', 'CreateClause', 'DeleteClause', 'PatternPath',
    'NodePattern', 'RelationshipPattern', 'WhereClause', 'ReturnClause',
    'OrderByClause', 'LimitClause', 'Expression', 'FunctionCall',
    'LogicalExpression', 'Condition', 'ReturnItem', 'OrderItem'
]
