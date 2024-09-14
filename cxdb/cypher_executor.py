# cxdb/cypher_executor.py

from cxdb.cypher_parser import CypherParser
from cxdb.core import CXDB
import re

class CypherQueryExecutor:
    def __init__(self, db: CXDB):
        self.db = db
        self.parser = CypherParser()

    def execute(self, query: str):
        try:
            ast = self.parser.parse(query)
            return self._execute_query(ast)
        except Exception as e:
            # If parsing fails, fall back to the old execution method
            return self._legacy_execute(query)

    def _execute_query(self, query):
        if hasattr(query, 'match'):
            return self._execute_match(query.match, query.where, query.return_)
        # Add handlers for other types of queries (CREATE, DELETE, etc.) as they are implemented in the parser
        raise ValueError(f"Unsupported query type: {type(query)}")

    def _legacy_execute(self, query):
        parts = query.strip().split(maxsplit=1)
        operation = parts[0].upper()

        if operation == 'CREATE':
            return self._execute_create(parts[1])
        elif operation == 'DELETE':
            return self._execute_delete(parts[1])
        else:
            raise ValueError(f"Unsupported operation: {operation}")

    def _execute_match(self, match, where, return_):
        matched_nodes = self._find_matching_nodes(match.pattern)
        if where:
            matched_nodes = self._apply_where_clause(matched_nodes, where)
        return self._process_return_clause(matched_nodes, return_)

    def _find_matching_nodes(self, pattern):
        node_type = pattern.label
        return self.db.nodes[self.db.nodes['type'] == node_type]

    def _apply_where_clause(self, nodes, where):
        property_name = where.condition.property_access.property
        property_value = where.condition.value.strip("'\"")
        return nodes[nodes['properties'].apply(lambda x: self._evaluate_condition(x, (property_name, property_value)))]

    def _process_return_clause(self, nodes, return_):
        result = []
        for _, node in nodes.iterrows():
            row = {}
            for item in return_.items:
                if '.' in item.expression:
                    node_prop, prop = item.expression.split('.')
                    row[item.alias] = node['properties'].get(prop)
                else:
                    row[item.alias] = node[item.expression]
            result.append(row)
        return result

    def _execute_create(self, query):
        match = re.match(r'\(n:(\w+)\s*\{(.+?)\}\)', query)
        if not match:
            raise ValueError("Unsupported CREATE query format")

        label, properties_str = match.groups()
        properties = self._parse_properties(properties_str)

        node_id = self.db.add_node(f"Node_{self.db.next_node_id}", label, properties)
        return node_id

    def _execute_delete(self, query):
        match = re.match(r'\(n\)\s+WHERE\s+(.+)', query)
        if not match:
            raise ValueError("Unsupported DELETE query format")

        where_clause = match.group(1)
        conditions = self._parse_where_clause(where_clause)

        nodes_to_delete = [
            node for _, node in self.db.nodes.iterrows() 
            if all(self._evaluate_condition(node['properties'], cond) for cond in conditions)
        ]

        deleted_count = 0
        for node in nodes_to_delete:
            self.db.delete_node(node['id'])
            deleted_count += 1

        return deleted_count

    def _parse_where_clause(self, where_clause):
        conditions = []
        for condition in where_clause.split('AND'):
            match = re.match(r'n\.(\w+)\s*=\s*([\'"]?.+?[\'"]?)$', condition.strip())
            if match:
                property_name, property_value = match.groups()
                conditions.append((property_name, property_value.strip("'\"")))
            else:
                raise ValueError(f"Invalid condition in WHERE clause: {condition}")
        return conditions

    def _evaluate_condition(self, properties, condition):
        property_name, property_value = condition
        node_value = properties.get(property_name)
        if node_value is None:
            return False
        if isinstance(node_value, (int, float)):
            try:
                property_value = type(node_value)(property_value)
            except ValueError:
                return False
        return str(node_value) == str(property_value)

    def _parse_properties(self, properties_str):
        properties = {}
        for prop in properties_str.split(','):
            key, value = prop.split(':')
            key = key.strip()
            value = value.strip().strip("'\"")
            try:
                value = int(value)
            except ValueError:
                try:
                    value = float(value)
                except ValueError:
                    pass
            properties[key] = value
        return properties