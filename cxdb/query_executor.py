# cxdb/query_executor.py

from cxdb.cypher_parser import CypherParser, CreateClause, DeleteClause, MatchClause

class CypherQueryExecutor:
    def __init__(self, db):
        self.db = db
        self.parser = CypherParser()

    def execute(self, query: str):
        ast = self.parser.parse(query)
        return self._execute_query(ast)

    def _execute_query(self, query):
        if isinstance(query, MatchClause):
            return self._execute_match(query.pattern, query.where, query.return_)
        elif isinstance(query, CreateClause):
            return self._execute_create(query.node_pattern)
        elif isinstance(query, DeleteClause):
            return self._execute_delete(query.node_pattern, query.where)
        else:
            raise ValueError(f"Unsupported query type: {type(query)}")

    def _execute_create(self, node_pattern):
        label = node_pattern.label
        properties = node_pattern.properties
        node_id = self.db.add_node(f"Node_{self.db.next_node_id}", label, properties)
        return node_id

    def _execute_delete(self, node_pattern, where):
        matching_nodes = self._find_matching_nodes(node_pattern)
        if where:
            matching_nodes = self._apply_where_clause(matching_nodes, where)
        
        deleted_count = 0
        for _, node in matching_nodes.iterrows():
            self.db.delete_node(node['id'])
            deleted_count += 1
        
        return deleted_count

    def _execute_match(self, match, where, return_):
        matched_nodes = self._find_matching_nodes(match)
        if where:
            matched_nodes = self._apply_where_clause(matched_nodes, where)
        return self._process_return_clause(matched_nodes, return_)

    def _find_matching_nodes(self, node_pattern):
        node_type = node_pattern.label
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