"""
Cypher Abstract Syntax Tree (AST) Module

This module defines the AST node classes used to represent the structure
of Cypher queries after parsing. These classes are used by the CypherParser
to construct the AST.

Classes:
    Query, MatchClause, CreateClause, DeleteClause, PatternPath, NodePattern,
    RelationshipPattern, WhereClause, ReturnClause, OrderByClause, LimitClause,
    Expression, FunctionCall, LogicalExpression, Condition
"""

class Query:
    def __init__(self, clauses):
        self.clauses = clauses

class MatchClause:
    def __init__(self, pattern_path, where):
        self.pattern_path = pattern_path
        self.where = where

class CreateClause:
    def __init__(self, pattern):
        self.pattern = pattern

class DeleteClause:
    def __init__(self, expressions, detach):
        self.expressions = expressions
        self.detach = detach

class PatternPath:
    def __init__(self, variable, pattern):
        self.variable = variable
        self.pattern = pattern

class NodePattern:
    def __init__(self, identifier, label, properties):
        self.identifier = identifier
        self.label = label
        self.properties = properties or {}

class RelationshipPattern:
    def __init__(self, identifier, label, properties, length, direction):
        self.identifier = identifier
        self.label = label
        self.properties = properties or {}
        self.length = length
        self.direction = direction

class WhereClause:
    def __init__(self, boolean_expr):
        self.boolean_expr = boolean_expr

class ReturnClause:
    def __init__(self, items, distinct):
        self.items = items
        self.distinct = distinct

class OrderByClause:
    def __init__(self, items):
        self.items = items

class LimitClause:
    def __init__(self, limit):
        self.limit = limit

class Expression:
    def __init__(self, value):
        self.value = value

class FunctionCall:
    def __init__(self, function_name, arguments):
        self.function_name = function_name
        self.arguments = arguments

class LogicalExpression:
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

class Condition:
    def __init__(self, identifier, property_, operator, value):
        self.identifier = identifier
        self.property = property_
        self.operator = operator
        self.value = value

# Export all classes
__all__ = [
    'Query', 'MatchClause', 'CreateClause', 'DeleteClause', 'PatternPath',
    'NodePattern', 'RelationshipPattern', 'WhereClause', 'ReturnClause',
    'OrderByClause', 'LimitClause', 'Expression', 'FunctionCall',
    'LogicalExpression', 'Condition'
]