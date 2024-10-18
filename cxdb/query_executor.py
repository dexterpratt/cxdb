# cxdb/query_executor.py

from cxdb.cypher_parser import CypherParser
from cxdb.cypher_ast import *

class CypherQueryExecutor:
    def __init__(self, db):
        self.db = db
        self.parser = CypherParser()

    def execute(self, query: str):
        """
        Execute a Cypher query string.
        """
        ast = self.parser.parse(query)
        return self._execute_query(ast)

    def _execute_query(self, query):
        """
        Execute a parsed Cypher query (AST).
        """
        result = None
        for clause in query.clauses:
            if isinstance(clause, MatchClause):
                result = self._execute_match(clause)
            elif isinstance(clause, CreateClause):
                result = self._execute_create(clause)
            elif isinstance(clause, DeleteClause):
                result = self._execute_delete(clause)
            elif isinstance(clause, ReturnClause):
                result = self._execute_return(clause, result)
            elif isinstance(clause, OrderByClause):
                result = self._execute_order_by(clause, result)
            elif isinstance(clause, LimitClause):
                result = self._execute_limit(clause, result)
        return result

    def _execute_match(self, match_clause):
        """
        Execute a MATCH clause.
        """
        pattern = match_clause.pattern_path.elements
        where = match_clause.where
        matched_elements = self._find_matching_elements(pattern)
        if where:
            matched_elements = self._apply_where_clause(matched_elements, where)
        return matched_elements

    def _execute_create(self, create_clause):
        """
        Execute a CREATE clause.
        """
        created_elements = []
        for element in create_clause.pattern:
            if isinstance(element, NodePattern):
                node_id = self.db.add_node(f"Node_{self.db.next_node_id}", element.label, element.properties)
                created_elements.append(('node', node_id))
            elif isinstance(element, RelationshipPattern):
                start_node = created_elements[-1][1]
                end_node = created_elements[-2][1] if len(created_elements) > 1 else None
                rel_id = self.db.add_relationship(start_node, end_node, element.label, element.properties)
                created_elements.append(('relationship', rel_id))
        return created_elements

    def _execute_delete(self, delete_clause):
        """
        Execute a DELETE clause.
        """
        deleted_count = 0
        for expr in delete_clause.expressions:
            element_id = self._evaluate_expression(expr)
            if element_id:
                if delete_clause.detach:
                    self.db.delete_node_with_relationships(element_id)
                else:
                    self.db.delete_node(element_id)
                deleted_count += 1
        return deleted_count

    def _execute_return(self, return_clause, input_data):
        """
        Execute a RETURN clause.
        """
        result = []
        for item in return_clause.items:
            if isinstance(item.expression, str):
                if '.' in item.expression:
                    entity, prop = item.expression.split('.')
                    for element in input_data:
                        result.append({item.alias or item.expression: self._get_element_property(element, entity, prop)})
                else:
                    for element in input_data:
                        result.append({item.alias or item.expression: element.get(item.expression)})
            else:
                for element in input_data:
                    result.append({item.alias or 'result': self._evaluate_expression(item.expression, element)})
        return result

    def _execute_order_by(self, order_by_clause, input_data):
        """
        Execute an ORDER BY clause.
        """
        def sort_key(item):
            return [self._evaluate_expression(order_item.expression, item) for order_item in order_by_clause.items]

        return sorted(input_data, key=sort_key, reverse=any(item.order == 'DESC' for item in order_by_clause.items))

    def _execute_limit(self, limit_clause, input_data):
        """
        Execute a LIMIT clause.
        """
        return input_data[:limit_clause.limit]

    def _find_matching_elements(self, pattern):
        """
        Find elements (nodes and relationships) matching the given pattern.
        """
        matched_elements = []
        for element in pattern:
            if isinstance(element, NodePattern):
                matched_nodes = self._find_matching_nodes(element)
                matched_elements.append(matched_nodes)
            elif isinstance(element, RelationshipPattern):
                matched_relationships = self._find_matching_relationships(element)
                matched_elements.append(matched_relationships)
        
        return self._combine_matched_elements(matched_elements)

    def _find_matching_nodes(self, node_pattern):
        """
        Find nodes matching the given node pattern.
        """
        return [node for node in self.db.nodes if self._node_matches_pattern(node, node_pattern)]

    def _find_matching_relationships(self, rel_pattern):
        """
        Find relationships matching the given relationship pattern.
        """
        return [rel for rel in self.db.relationships if self._relationship_matches_pattern(rel, rel_pattern)]

    def _node_matches_pattern(self, node, pattern):
        """
        Check if a node matches the given pattern.
        """
        if pattern.label and node['type'] != pattern.label:
            return False
        return all(node['properties'].get(key) == value for key, value in pattern.properties.items())

    def _relationship_matches_pattern(self, rel, pattern):
        """
        Check if a relationship matches the given pattern.
        """
        if pattern.label and rel['type'] != pattern.label:
            return False
        return all(rel['properties'].get(key) == value for key, value in pattern.properties.items())

    def _combine_matched_elements(self, matched_elements):
        """
        Combine matched elements into valid paths.
        This is a simplified implementation and may need to be enhanced for complex queries.
        """
        if len(matched_elements) == 1:
            return matched_elements[0]
        
        combined = []
        for node in matched_elements[0]:
            path = [node]
            for i in range(1, len(matched_elements), 2):
                rel = next((r for r in matched_elements[i] if r['start_node'] == node['id']), None)
                if rel:
                    path.append(rel)
                    next_node = next((n for n in matched_elements[i+1] if n['id'] == rel['end_node']), None)
                    if next_node:
                        path.append(next_node)
                        node = next_node
                    else:
                        break
                else:
                    break
            if len(path) == len(matched_elements):
                combined.append(path)
        
        return combined

    def _apply_where_clause(self, elements, where):
        """
        Apply a WHERE clause to filter elements.
        """
        return [element for element in elements if self._evaluate_expression(where.boolean_expr, element)]

    def _evaluate_expression(self, expr, context=None):
        """
        Evaluate an expression in the given context.
        """
        if isinstance(expr, Expression):
            if isinstance(expr.value, str):
                if context and '.' in expr.value:
                    entity, prop = expr.value.split('.')
                    return self._get_element_property(context, entity, prop)
                return expr.value.strip("'")  # Remove quotes from string literals
            elif isinstance(expr.value, tuple):
                operator, left, right = expr.value
                left_value = self._evaluate_expression(left, context)
                right_value = self._evaluate_expression(right, context)
                if operator == 'PLUS':
                    return left_value + right_value
                elif operator == 'CONTAINS':
                    return right_value in left_value
                elif operator == 'ENDS_WITH':
                    return left_value.endswith(right_value)
            return expr.value
        elif isinstance(expr, LogicalExpression):
            left = self._evaluate_expression(expr.left, context)
            right = self._evaluate_expression(expr.right, context)
            if expr.operator == 'AND':
                return left and right
            elif expr.operator == 'OR':
                return left or right
        elif isinstance(expr, Condition):
            left = self._evaluate_expression(expr.left, context)
            right = self._evaluate_expression(expr.right, context)
            if expr.operator == '=':
                return left == right
            elif expr.operator == '>':
                return left > right
            elif expr.operator == '<':
                return left < right
        return None

    def _get_element_property(self, element, entity, prop):
        """
        Get a property value from an element (node or relationship).
        """
        if isinstance(element, dict):
            return element.get('properties', {}).get(prop)
        elif isinstance(element, list):  # For path results
            for item in element:
                if item.get('id') == entity:
                    return item.get('properties', {}).get(prop)
        return None
