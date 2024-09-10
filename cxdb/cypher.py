# cxdb/cypher.py
# https://neo4j.com/docs/cypher-manual/current/queries/expressions/

import re

class CypherExecutor:
    def __init__(self, cxdb):
        self.cxdb = cxdb

    def execute(self, query):
        parts = query.strip().split(maxsplit=1)
        operation = parts[0].upper()

        if operation == 'MATCH':
            return self._execute_match(parts[1])
        elif operation == 'CREATE':
            return self._execute_create(parts[1])
        elif operation == 'DELETE':
            return self._execute_delete(parts[1])
        else:
            raise ValueError(f"Unsupported operation: {operation}")

    def _execute_match(self, query):
        match = re.match(r'\(n\)\s+WHERE\s+(.+?)\s+RETURN\s+n', query)
        if not match:
            raise ValueError("Unsupported MATCH query format")

        where_clause = match.group(1)
        conditions = self._parse_where_clause(where_clause)

        matching_nodes = [
            node for _, node in self.cxdb.nodes.iterrows() 
            if all(self._evaluate_condition(node['properties'], cond) for cond in conditions)
        ]
        return matching_nodes

    def _execute_create(self, query):
        match = re.match(r'\(n:(\w+)\s*\{(.+?)\}\)', query)
        if not match:
            raise ValueError("Unsupported CREATE query format")

        label, properties_str = match.groups()
        properties = self._parse_properties(properties_str)

        node_id = self.cxdb.add_node(f"Node_{self.cxdb.next_node_id}", label, properties)
        return node_id

    def _execute_delete(self, query):
        match = re.match(r'\(n\)\s+WHERE\s+(.+)', query)
        if not match:
            raise ValueError("Unsupported DELETE query format")

        where_clause = match.group(1)
        conditions = self._parse_where_clause(where_clause)

        nodes_to_delete = [
            node for _, node in self.cxdb.nodes.iterrows() 
            if all(self._evaluate_condition(node['properties'], cond) for cond in conditions)
        ]

        deleted_count = 0
        for node in nodes_to_delete:
            self.cxdb.delete_node(node['id'])
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