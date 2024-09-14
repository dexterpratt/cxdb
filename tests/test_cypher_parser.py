import pytest
from cxdb.cypher_parser import CypherParser, MatchClause
from cxdb.cypher_exceptions import CypherSyntaxError, CypherSemanticError

@pytest.fixture
def parser():
    return CypherParser()

def test_lexer_initialization(parser):
    assert parser.lexer.lexer is not None
    
    # Test a simple token
    parser.lexer.lexer.input("MATCH")
    token = parser.lexer.lexer.token()
    assert token.type == "MATCH"
    assert token.value == "MATCH"

def test_simple_match(parser):
    query = "MATCH (n:Person) RETURN n"
    result = parser.parse(query)
    assert result is not None
    assert isinstance(result, MatchClause)
    assert result.match is not None
    assert result.match.label == 'Person'
    assert result.return_ is not None

def test_match_with_where(parser):
    query = "MATCH (n:Person) WHERE n.name = 'John' RETURN n.name"
    result = parser.parse(query)
    assert result is not None
    assert result.match is not None
    assert result.where is not None
    assert result.return_ is not None

def test_return_with_alias(parser):
    query = "MATCH (n:Person) RETURN n.name AS name"
    result = parser.parse(query)
    assert result is not None
    assert result.return_ is not None
    assert len(result.return_.items) == 1
    assert result.return_.items[0].expression == 'n.name'
    assert result.return_.items[0].alias == 'name'

def test_syntax_error(parser):
    query = "MATCH (n:Person) RETURN"
    with pytest.raises(CypherSyntaxError) as excinfo:
        parser.parse(query)
    assert "Incomplete RETURN clause" in str(excinfo.value)

def test_semantic_error(parser):
    query = "MATCH (n:Person) RETURN invalid.syntax"
    with pytest.raises(CypherSemanticError) as excinfo:
        parser.parse(query)
    assert "Invalid identifier 'invalid' in property access" in str(excinfo.value)