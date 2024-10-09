import unittest
from cxdb.cypher_parser import CypherParser
from cxdb.cypher_exceptions import CypherSyntaxError, CypherSemanticError
from cxdb.cypher_ast import (
    Query, MatchClause, CreateClause, DeleteClause, ReturnClause,
    OrderByClause, LimitClause, FunctionCall
)

class TestCypherParser(unittest.TestCase):
    def setUp(self):
        self.parser = CypherParser()

    def test_simple_match_query(self):
        query = "MATCH (n:Person) RETURN n"
        ast = self.parser.parse(query)
        self.assertIsNotNone(ast)
        self.assertEqual(len(ast.clauses), 2)
        self.assertIsInstance(ast.clauses[0], MatchClause)
        self.assertIsInstance(ast.clauses[1], ReturnClause)

    def test_match_where_query(self):
        query = "MATCH (n:Person) WHERE n.age > 30 RETURN n.name"
        ast = self.parser.parse(query)
        self.assertIsNotNone(ast)
        self.assertEqual(len(ast.clauses), 2)
        self.assertIsInstance(ast.clauses[0], MatchClause)
        self.assertIsNotNone(ast.clauses[0].where)
        self.assertIsInstance(ast.clauses[1], ReturnClause)

    def test_create_query(self):
        query = "CREATE (n:Person {name: 'John', age: 30})"
        ast = self.parser.parse(query)
        self.assertIsNotNone(ast)
        self.assertEqual(len(ast.clauses), 1)
        self.assertIsInstance(ast.clauses[0], CreateClause)

    def test_delete_query(self):
        query = "MATCH (n:Person) WHERE n.name = 'John' DELETE n"
        ast = self.parser.parse(query)
        self.assertIsNotNone(ast)
        self.assertEqual(len(ast.clauses), 2)
        self.assertIsInstance(ast.clauses[0], MatchClause)
        self.assertIsInstance(ast.clauses[1], DeleteClause)

    def test_complex_query(self):
        query = """
        MATCH (a:Person)-[:KNOWS]->(b:Person)
        WHERE a.age > 30 AND b.name = 'Alice'
        RETURN a.name, b.age
        ORDER BY a.name
        LIMIT 10
        """
        ast = self.parser.parse(query)
        self.assertIsNotNone(ast)
        self.assertEqual(len(ast.clauses), 4)
        self.assertIsInstance(ast.clauses[0], MatchClause)
        self.assertIsInstance(ast.clauses[1], ReturnClause)
        self.assertIsInstance(ast.clauses[2], OrderByClause)
        self.assertIsInstance(ast.clauses[3], LimitClause)

    def test_function_call(self):
        query = "MATCH (n:Person) RETURN count(n) AS person_count"
        ast = self.parser.parse(query)
        self.assertIsNotNone(ast)
        self.assertEqual(len(ast.clauses), 2)
        return_clause = ast.clauses[1]
        self.assertIsInstance(return_clause.items[0].expression, FunctionCall)
        self.assertEqual(return_clause.items[0].expression.function_name, 'count')

    def test_syntax_error(self):
        query = "MATCH (n:Person) RETURN n,"  # Missing expression after comma
        with self.assertRaises(CypherSyntaxError):
            self.parser.parse(query)

    def test_semantic_error_undefined_identifier(self):
        query = "MATCH (n:Person) RETURN m.name"  # 'm' is not defined
        with self.assertRaises(CypherSemanticError):
            self.parser.parse(query)

    def test_semantic_error_type_mismatch(self):
        query = "MATCH (n:Person) WHERE n.age > 'thirty' RETURN n"  # Comparing int with string
        with self.assertRaises(CypherSemanticError):
            self.parser.parse(query)

    def test_semantic_error_unknown_function(self):
        query = "MATCH (n:Person) RETURN unknown_func(n.name)"
        with self.assertRaises(CypherSemanticError):
            self.parser.parse(query)

if __name__ == '__main__':
    unittest.main()