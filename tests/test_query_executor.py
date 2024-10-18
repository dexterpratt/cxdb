import unittest
from cxdb.core import CXDB
from cxdb.query_executor import CypherQueryExecutor

class TestQueryExecutor(unittest.TestCase):
    def setUp(self):
        self.db = CXDB()
        self.executor = CypherQueryExecutor(self.db)

    def test_create_and_match_node(self):
        create_query = "CREATE (p:Person {name: 'John Doe', age: '30'})"
        self.executor.execute(create_query)

        match_query = "MATCH (p:Person) WHERE p.name = 'John Doe' RETURN p.name, p.age"
        result = self.executor.execute(match_query)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['p.name'], 'John Doe')
        self.assertEqual(result[0]['p.age'], '30')

    def test_create_multiple_nodes_and_match(self):
        create_queries = [
            "CREATE (p:Person {name: 'Alice', city: 'New York'})",
            "CREATE (p:Person {name: 'Bob', city: 'London'})",
            "CREATE (p:Person {name: 'Charlie', city: 'Paris'})"
        ]
        for query in create_queries:
            self.executor.execute(query)

        match_query = "MATCH (p:Person) WHERE p.city = 'London' RETURN p.name"
        result = self.executor.execute(match_query)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['p.name'], 'Bob')

    def test_create_and_delete_node(self):
        create_query = "CREATE (p:Person {name: 'Jane Doe', email: 'jane@example.com'})"
        self.executor.execute(create_query)

        delete_query = "MATCH (p:Person) WHERE p.email = 'jane@example.com' DELETE p"
        delete_result = self.executor.execute(delete_query)

        self.assertEqual(delete_result, 1)  # One node should be deleted

        match_query = "MATCH (p:Person) WHERE p.name = 'Jane Doe' RETURN p.name"
        match_result = self.executor.execute(match_query)

        self.assertEqual(len(match_result), 0)  # No nodes should be found

    def test_complex_where_clause(self):
        create_queries = [
            "CREATE (p:Person {name: 'Alice', age: '25', city: 'New York'})",
            "CREATE (p:Person {name: 'Bob', age: '30', city: 'London'})",
            "CREATE (p:Person {name: 'Charlie', age: '35', city: 'Paris'})"
        ]
        for query in create_queries:
            self.executor.execute(query)

        complex_query = """
        MATCH (p:Person)
        WHERE p.age > '25' AND (p.city = 'London' OR p.city = 'Paris')
        RETURN p.name, p.age, p.city
        """
        result = self.executor.execute(complex_query)

        self.assertEqual(len(result), 2)
        self.assertIn({'p.name': 'Bob', 'p.age': '30', 'p.city': 'London'}, result)
        self.assertIn({'p.name': 'Charlie', 'p.age': '35', 'p.city': 'Paris'}, result)

    def test_order_by_and_limit(self):
        create_queries = [
            "CREATE (p:Person {name: 'Alice', age: '25'})",
            "CREATE (p:Person {name: 'Bob', age: '30'})",
            "CREATE (p:Person {name: 'Charlie', age: '35'})",
            "CREATE (p:Person {name: 'David', age: '40'})"
        ]
        for query in create_queries:
            self.executor.execute(query)

        query = """
        MATCH (p:Person)
        RETURN p.name, p.age
        ORDER BY p.age DESC
        LIMIT 2
        """
        result = self.executor.execute(query)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['p.name'], 'David')
        self.assertEqual(result[1]['p.name'], 'Charlie')

    def test_string_operations(self):
        create_queries = [
            "CREATE (p:Person {name: 'Alice Johnson', email: 'alice@example.com'})",
            "CREATE (p:Person {name: 'Bob Smith', email: 'bob@example.com'})",
            "CREATE (p:Person {name: 'Charlie Brown', email: 'charlie@example.com'})"
        ]
        for query in create_queries:
            self.executor.execute(query)

        query = """
        MATCH (p:Person)
        WHERE p.name CONTAINS 'Smith' OR p.email ENDS WITH '@example.com'
        RETURN p.name, p.email
        """
        result = self.executor.execute(query)

        self.assertEqual(len(result), 3)
        self.assertIn({'p.name': 'Alice Johnson', 'p.email': 'alice@example.com'}, result)
        self.assertIn({'p.name': 'Bob Smith', 'p.email': 'bob@example.com'}, result)
        self.assertIn({'p.name': 'Charlie Brown', 'p.email': 'charlie@example.com'}, result)

    def test_create_and_match_relationship(self):
        create_query = """
        CREATE (a:Person {name: 'Alice'})-[r:KNOWS {since: '2020'}]->(b:Person {name: 'Bob'})
        """
        self.executor.execute(create_query)

        match_query = """
        MATCH (a:Person)-[r:KNOWS]->(b:Person)
        RETURN a.name, r.since, b.name
        """
        result = self.executor.execute(match_query)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['a.name'], 'Alice')
        self.assertEqual(result[0]['r.since'], '2020')
        self.assertEqual(result[0]['b.name'], 'Bob')

    def test_match_relationship_with_properties(self):
        create_queries = [
            "CREATE (a:Person {name: 'Alice'})-[r:KNOWS {since: '2020'}]->(b:Person {name: 'Bob'})",
            "CREATE (c:Person {name: 'Charlie'})-[r:KNOWS {since: '2021'}]->(d:Person {name: 'David'})"
        ]
        for query in create_queries:
            self.executor.execute(query)

        match_query = """
        MATCH (a:Person)-[r:KNOWS {since: '2020'}]->(b:Person)
        RETURN a.name, b.name
        """
        result = self.executor.execute(match_query)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['a.name'], 'Alice')
        self.assertEqual(result[0]['b.name'], 'Bob')

    def test_match_multiple_relationships(self):
        create_query = """
        CREATE (a:Person {name: 'Alice'})-[:KNOWS]->(b:Person {name: 'Bob'}),
               (b)-[:KNOWS]->(c:Person {name: 'Charlie'}),
               (c)-[:KNOWS]->(d:Person {name: 'David'})
        """
        self.executor.execute(create_query)

        match_query = """
        MATCH (a:Person {name: 'Alice'})-[:KNOWS*2..3]->(b:Person)
        RETURN b.name
        """
        result = self.executor.execute(match_query)

        self.assertEqual(len(result), 2)
        names = [r['b.name'] for r in result]
        self.assertIn('Charlie', names)
        self.assertIn('David', names)

if __name__ == '__main__':
    unittest.main()
