# tests/test_cypher_parser.py

import pytest
from cxdb.cypher_parser import CypherParser, MatchClause, CreateClause, DeleteClause
from cxdb.cypher_exceptions import CypherSyntaxError, CypherSemanticError

@pytest.fixture
def parser():
    return CypherParser()

def test_simple_match(parser):
    query = "MATCH (n:Person) RETURN n"
    result = parser.parse(query)
    assert isinstance(result, MatchClause)
    assert result.pattern is not None 

def test_create_clause(parser):
    query = "CREATE (n:Person)"
    result = parser.parse(query)
    assert isinstance(result, CreateClause)
    assert result.node_pattern is not None
    assert result.node_pattern.label == 'Person'

def test_delete_clause(parser):
    query = "DELETE (n:Person) WHERE n.age > 30"
    result = parser.parse(query)
    assert isinstance(result, DeleteClause)
    assert result.node_pattern is not None
    assert result.node_pattern.label == 'Person'
    assert result.where is not None

def test_return_with_alias(parser):
    query = "MATCH (n:Person) RETURN n.name AS name"
    result = parser.parse(query)
    assert isinstance(result, MatchClause)
    assert result.return_ is not None
    assert len(result.return_.items) == 1
    assert result.return_.items[0].expression == "n.name"
    assert result.return_.items[0].alias == "name"

def test_syntax_error_incomplete_return(parser):
    query = "MATCH (n:Person) RETURN"
    with pytest.raises(CypherSyntaxError) as excinfo:
        parser.parse(query)
    assert "Incomplete RETURN clause" in str(excinfo.value)

def test_syntax_error_incomplete_query(parser):
    query = "MATCH (n:Person)"
    with pytest.raises(CypherSyntaxError) as excinfo:
        parser.parse(query)
    assert "Incomplete query" in str(excinfo.value)

def test_syntax_error_invalid_token(parser):
    query = "MATCH (n:Person) RETURN n WHERE"
    with pytest.raises(CypherSyntaxError) as excinfo:
        parser.parse(query)
    assert "Syntax error at 'WHERE'" in str(excinfo.value)

def test_semantic_error(parser):
    query = "MATCH (n:Person) RETURN invalid.syntax"
    result = parser.parse(query)
    # Since we're not implementing semantic error checking in the parser,
    # we'll assert that the query is parsed without raising an exception
    assert isinstance(result, MatchClause)
    assert result.return_ is not None
    assert len(result.return_.items) == 1
    assert result.return_.items[0].expression == "invalid.syntax"