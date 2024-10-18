import pytest
from cxdb.cypher_parser import CypherParser
from cxdb.cypher_exceptions import CypherSyntaxError, CypherSemanticError

class TestCypherParser:
    def setup_method(self):
        self.parser = CypherParser()

    def test_simple_match_query(self):
        query = "MATCH (n:Person) RETURN n"
        ast = self.parser.parse(query)
        assert ast is not None

    def test_match_where_query(self):
        query = "MATCH (n:Person) WHERE n.age > 30 RETURN n.name"
        ast = self.parser.parse(query)
        assert ast is not None

    def test_create_query(self):
        query = "CREATE (n:Person {name: 'John', age: 30})"
        ast = self.parser.parse(query)
        assert ast is not None

    def test_delete_query(self):
        query = "MATCH (n:Person) WHERE n.name = 'John' DELETE n"
        ast = self.parser.parse(query)
        assert ast is not None

    def test_complex_query(self):
        query = """
        MATCH (a:Person)-[:KNOWS]->(b:Person)
        WHERE a.age > 30 AND b.name = 'Alice'
        RETURN a.name, b.age
        ORDER BY a.name
        LIMIT 10
        """
        ast = self.parser.parse(query)
        assert ast is not None

    def test_function_call(self):
        query = "MATCH (n:Person) RETURN count(n) AS person_count"
        ast = self.parser.parse(query)
        assert ast is not None

    def test_syntax_error(self):
        query = "MATCH (n:Person) RETURN n,"  # Missing expression after comma
        with pytest.raises(CypherSyntaxError):
            self.parser.parse(query)

    def test_semantic_error_undefined_identifier(self):
        query = "MATCH (n:Person) RETURN m.name"  # 'm' is not defined
        with pytest.raises(CypherSemanticError):
            self.parser.parse(query)

    def test_semantic_error_invalid_function(self):
        query = "MATCH (n:Person) RETURN invalid_function(n.name)"
        with pytest.raises(CypherSemanticError):
            self.parser.parse(query)

    def test_property_comparison(self):
        query = "MATCH (n:Person) WHERE n.age > 'thirty' RETURN n"
        ast = self.parser.parse(query)
        assert ast is not None

    # New tests for updated Condition and semantic analyzer
    def test_complex_condition(self):
        query = "MATCH (n:Person) WHERE n.age > 30 AND n.name STARTS WITH 'J' RETURN n"
        ast = self.parser.parse(query)
        assert ast is not None

    def test_multiple_conditions(self):
        query = "MATCH (n:Person) WHERE n.age > 30 AND n.name = 'John' OR n.city = 'New York' RETURN n"
        ast = self.parser.parse(query)
        assert ast is not None

    def test_nested_conditions(self):
        query = "MATCH (n:Person) WHERE (n.age > 30 AND n.name = 'John') OR (n.age < 20 AND n.name = 'Alice') RETURN n"
        ast = self.parser.parse(query)
        assert ast is not None

    def test_condition_with_function(self):
        query = "MATCH (n:Person) WHERE length(n.name) > 5 RETURN n"
        ast = self.parser.parse(query)
        assert ast is not None

    # Right now, we allow properties to be compared with anything. 
    # 
    # def test_semantic_error_invalid_operator(self):
    #     query = "MATCH (n:Person) WHERE n.age > 'old' RETURN n"
    #     with pytest.raises(CypherSemanticError):
    #         self.parser.parse(query)

    # I'm not sure which issue is supposed to raise an error.
    # name is probably a string, but we don't know that. 
    # So we probably will get poor error reporting in the case of math operators called on strings
    # def test_semantic_error_type_mismatch(self):
    #     query = "MATCH (n:Person) WHERE n.age + n.name > 30 RETURN n"
    #     with pytest.raises(CypherSemanticError):
    #         self.parser.parse(query)

    def test_property_access_in_return(self):
        query = "MATCH (n:Person) RETURN n.name, n.age"
        ast = self.parser.parse(query)
        assert ast is not None

    def test_relationship_property(self):
        query = "MATCH (a:Person)-[r:KNOWS]->(b:Person) WHERE r.since > 2010 RETURN a, b"
        ast = self.parser.parse(query)
        assert ast is not None
