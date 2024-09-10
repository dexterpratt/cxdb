# tests/test_cypher_parser.py

import pytest
from cxdb.cypher_parser import CypherParser, Query, MatchClause, WhereClause, ReturnClause
from cxdb.cypher_exceptions import CypherLexerError, CypherSyntaxError, CypherSemanticError

@pytest.fixture
def parser():
    return CypherParser()

def test_simple_match(parser):
    query = "MATCH (n:Person) RETURN n"
    ast = parser.parse(query)
    assert isinstance(ast, Query)
    assert isinstance(ast.match, MatchClause)
    assert ast.where is None
    assert isinstance(ast.return_, ReturnClause)

def test_match_with_where(parser):
    query = "MATCH (n:Person) WHERE n.name = 'John' RETURN n.name"
    ast = parser.parse(query)
    assert isinstance(ast, Query)
    assert isinstance(ast.match, MatchClause)
    assert isinstance(ast.where, WhereClause)
    assert isinstance(ast.where.condition, Condition)
    assert isinstance(ast.where.condition.property_access, PropertyAccess)
    assert ast.where.condition.property_access.identifier == 'n'
    assert ast.where.condition.property_access.property == 'name'
    assert ast.where.condition.value == 'John'
    assert isinstance(ast.return_, ReturnClause)

def test_return_with_alias(parser):
    query = "MATCH (n:Person) RETURN n.name AS name"
    ast = parser.parse(query)
    assert isinstance(ast.return_, ReturnClause)
    assert len(ast.return_.items) == 1
    assert ast.return_.items[0].expression == 'n.name'
    assert ast.return_.items[0].alias == 'name'

def test_lexer_error(parser):
    query = "MATCH (n@Person) RETURN n"
    with pytest.raises(CypherLexerError):
        parser.parse(query)

def test_syntax_error(parser):
    query = "MATCH (n:Person) RETURN"
    with pytest.raises(CypherSyntaxError):
        parser.parse(query)

def test_semantic_error(parser):
    query = "MATCH (n:Person) RETURN"
    with pytest.raises(CypherSemanticError):
        parser.parse(query)