"""
Cypher Semantic Analyzer Module

This module provides semantic analysis functionality for Cypher queries.
It checks for semantic correctness of the parsed Abstract Syntax Tree (AST).
"""

from cxdb.cypher_exceptions import CypherSemanticError

class CypherSemanticAnalyzer:
    # List of built-in functions with their return types
    built_in_functions = {
        'count': 'INTEGER',
        'sum': 'FLOAT',
        'avg': 'FLOAT',
        'max': 'ANY',
        'min': 'ANY',
        'collect': 'LIST',
        'length': 'INTEGER',
        'type': 'STRING',
        'id': 'INTEGER',
        'toInteger': 'INTEGER',
        'toFloat': 'FLOAT',
        'toString': 'STRING'
    }

    def __init__(self):
        self.symbol_table = {}
        self.current_scope = 'global'

    def check_semantics(self, ast):
        """
        Perform semantic analysis on the AST.
        """
        ast.check_semantics(self)

    def add_symbol(self, name, symbol_type):
        """
        Add a symbol to the symbol table or update its type if it already exists.
        """
        self.symbol_table[name] = symbol_type

    def get_symbol_type(self, name):
        """
        Get the type of a symbol from the symbol table.
        """
        if name not in self.symbol_table:
            raise CypherSemanticError(f"Symbol '{name}' not defined")
        return self.symbol_table[name]

    def symbol_exists(self, name):
        """
        Check if a symbol exists in the symbol table.
        """
        return name in self.symbol_table

    def enter_scope(self, scope_name):
        """
        Enter a new scope.
        """
        self.current_scope = scope_name

    def exit_scope(self):
        """
        Exit the current scope.
        """
        self.current_scope = 'global'

    def check_function_call(self, function_call):
        """
        Check the semantic correctness of a function call.
        """
        if function_call.function_name not in self.built_in_functions:
            raise CypherSemanticError(f"Unknown function '{function_call.function_name}'")
        return self.built_in_functions[function_call.function_name]

    def is_property_access(self, value):
        """
        Check if a value represents a property access.
        """
        if isinstance(value, str):
            return '.' in value
        elif hasattr(value, 'value'):  # For Expression objects
            return self.is_property_access(value.value)
        return False

    def is_string_literal(self, value):
        return isinstance(value, str) and not "." in value #value.startswith("'") and value.endswith("'")

    def check_type_match(self, node):
        """
        Check for type mismatches in comparisons.
        """
        if hasattr(node, 'operator') and node.operator in ['AND', 'OR']:
            # For logical expressions, check each side separately
            self.check_type_match(node.left)
            self.check_type_match(node.right)
            return

        left_type = self.get_type(node.left)
        right_type = self.get_type(node.right)
        
        # Allow comparisons between properties and literals
        if left_type == 'PROPERTY' or right_type == 'PROPERTY':
            return
        
        # Allow comparisons between ANY and any other type
        if left_type == 'ANY' or right_type == 'ANY':
            return
        
        if left_type != right_type:
            raise CypherSemanticError(f"Type mismatch in comparison: {left_type} and {right_type}")

    def get_type(self, value):
        """
        Get the type of a value or expression.
        """
        if isinstance(value, int):
            return 'INTEGER'
        elif isinstance(value, float):
            return 'FLOAT'
        elif isinstance(value, bool):
            return 'BOOLEAN'
        elif isinstance(value, str):
            if self.is_property_access(value):
                return 'PROPERTY'
            elif self.is_string_literal(value):
                return 'STRING'
            else:
                return 'IDENTIFIER'  # This could be a variable or a label
        elif hasattr(value, 'value'):  # For Expression nodes
            if isinstance(value.value, tuple) and value.value[0] == 'PLUS':
                left_type = self.get_type(value.value[1])
                right_type = self.get_type(value.value[2])
                if left_type != right_type:
                    raise CypherSemanticError(f"Type mismatch in addition: {left_type} and {right_type}")
                return left_type
            return self.get_type(value.value)
        elif hasattr(value, 'function_name'):  # For FunctionCall nodes
            return self.check_function_call(value)
        elif hasattr(value, 'name'):
            return self.get_symbol_type(value.name)
        elif hasattr(value, 'left') and hasattr(value, 'right'):  # For LogicalExpression nodes
            return 'BOOLEAN'  # Logical expressions always result in a boolean
        else:
            return 'UNKNOWN'

    def get_property_type(self, property_access):
        """
        Get the type of a property. This is a placeholder and should be replaced with actual schema checking.
        """
        # For now, we'll return 'ANY' type for all properties to allow flexible comparisons
        return 'ANY'

    def check_condition(self, condition):
        """
        Check the semantic correctness of a condition.
        """
        left_type = self.get_type(condition.left)
        right_type = self.get_type(condition.right)

        # Allow comparisons between properties, literals, and identifiers
        if 'PROPERTY' in (left_type, right_type) or 'IDENTIFIER' in (left_type, right_type):
            return

        # Allow comparisons between ANY and any other type
        if 'ANY' in (left_type, right_type):
            return

        if left_type != right_type:
            raise CypherSemanticError(f"Type mismatch in condition: {left_type} and {right_type}")

        # Check if the operator is valid for the given types
        valid_operators = {
            'INTEGER': ['=', '<>', '<', '<=', '>', '>='],
            'FLOAT': ['=', '<>', '<', '<=', '>', '>='],
            'STRING': ['=', '<>', 'STARTS_WITH', 'ENDS_WITH', 'CONTAINS'],
            'BOOLEAN': ['=', '<>'],
            'PROPERTY': ['=', '<>', '<', '<=', '>', '>=', 'STARTS_WITH', 'ENDS_WITH', 'CONTAINS'],
            'IDENTIFIER': ['=', '<>', '<', '<=', '>', '>=', 'STARTS_WITH', 'ENDS_WITH', 'CONTAINS'],
            'ANY': ['=', '<>', '<', '<=', '>', '>=', 'STARTS_WITH', 'ENDS_WITH', 'CONTAINS']
        }

        if condition.operator not in valid_operators.get(left_type, []) and condition.operator not in valid_operators.get(right_type, []):
            raise CypherSemanticError(f"Invalid operator '{condition.operator}' for types {left_type} and {right_type}")

    # Add more semantic analysis methods as needed
