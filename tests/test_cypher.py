# tests/test_cypher.py

import pytest
from cxdb.core import CXDB
from cxdb.cypher import CypherExecutor

@pytest.fixture
def cxdb():
    return CXDB()

@pytest.fixture
def cypher_executor(cxdb):
    return CypherExecutor(cxdb)

def test_create_node(cypher_executor):
    result = cypher_executor.execute("CREATE (n:Person {name: 'John', age: 30})")
    assert result is not None
    node = cypher_executor.cxdb.get_node(result)
    assert node['type'] == 'Person'
    assert node['properties'] == {'name': 'John', 'age': 30}

def test_match_node(cypher_executor):
    cypher_executor.execute("CREATE (n:Person {name: 'John', age: 30})")
    cypher_executor.execute("CREATE (n:Person {name: 'Jane', age: 25})")
    result = cypher_executor.execute("MATCH (n) WHERE n.name = 'John' RETURN n")
    assert len(result) == 1
    assert result[0]['properties'] == {'name': 'John', 'age': 30}

def test_delete_node(cypher_executor):
    cypher_executor.execute("CREATE (n:Person {name: 'John', age: 30})")
    cypher_executor.execute("CREATE (n:Person {name: 'Jane', age: 25})")
    result = cypher_executor.execute("DELETE (n) WHERE n.name = 'John'")
    assert result == 1
    remaining = cypher_executor.execute("MATCH (n) WHERE n.name = 'John' RETURN n")
    assert len(remaining) == 0

def test_delete_multiple_nodes(cypher_executor):
    cypher_executor.execute("CREATE (n:Person {name: 'John', age: 30})")
    cypher_executor.execute("CREATE (n:Person {name: 'John', age: 25})")
    cypher_executor.execute("CREATE (n:Person {name: 'Jane', age: 28})")
    result = cypher_executor.execute("DELETE (n) WHERE n.name = 'John'")
    assert result == 2
    remaining = cypher_executor.execute("MATCH (n) WHERE n.name = 'John' RETURN n")
    assert len(remaining) == 0
    remaining = cypher_executor.execute("MATCH (n) WHERE n.name = 'Jane' RETURN n")
    assert len(remaining) == 1


def test_delete_with_multiple_conditions(cypher_executor):
    cypher_executor.execute("CREATE (n:Person {name: 'John', age: 30})")
    cypher_executor.execute("CREATE (n:Person {name: 'John', age: 25})")
    cypher_executor.execute("CREATE (n:Person {name: 'Jane', age: 30})")
    result = cypher_executor.execute("DELETE (n) WHERE n.name = 'John' AND n.age = 30")
    assert result == 1
    remaining = cypher_executor.execute("MATCH (n) WHERE n.name = 'John' RETURN n")
    assert len(remaining) == 1
    assert remaining[0]['properties']['age'] == 25

def test_match_with_multiple_conditions(cypher_executor):
    cypher_executor.execute("CREATE (n:Person {name: 'John', age: 30, city: 'New York'})")
    cypher_executor.execute("CREATE (n:Person {name: 'John', age: 25, city: 'Boston'})")
    cypher_executor.execute("CREATE (n:Person {name: 'Jane', age: 30, city: 'New York'})")
    result = cypher_executor.execute("MATCH (n) WHERE n.name = 'John' AND n.city = 'New York' RETURN n")
    assert len(result) == 1
    assert result[0]['properties'] == {'name': 'John', 'age': 30, 'city': 'New York'}

def test_match_with_numeric_condition(cypher_executor):
    cypher_executor.execute("CREATE (n:Person {name: 'John', age: 30})")
    cypher_executor.execute("CREATE (n:Person {name: 'Jane', age: 25})")
    result = cypher_executor.execute("MATCH (n) WHERE n.age = 30 RETURN n")
    assert len(result) == 1
    assert result[0]['properties'] == {'name': 'John', 'age': 30}

def test_unsupported_operation(cypher_executor):
    with pytest.raises(ValueError, match="Unsupported operation: UPDATE"):
        cypher_executor.execute("UPDATE (n) SET n.age = 31 WHERE n.name = 'John'")

def test_invalid_match_format(cypher_executor):
    with pytest.raises(ValueError, match="Unsupported MATCH query format"):
        cypher_executor.execute("MATCH (n) RETURN n")

def test_invalid_create_format(cypher_executor):
    with pytest.raises(ValueError, match="Unsupported CREATE query format"):
        cypher_executor.execute("CREATE n:Person")

def test_invalid_delete_format(cypher_executor):
    with pytest.raises(ValueError, match="Unsupported DELETE query format"):
        cypher_executor.execute("DELETE n")

def test_create_node_with_float(cypher_executor):
    result = cypher_executor.execute("CREATE (n:Person {name: 'John', height: 1.85})")
    assert result is not None
    node = cypher_executor.cxdb.get_node(result)
    assert node['type'] == 'Person'
    assert node['properties'] == {'name': 'John', 'height': 1.85}

def test_match_node_with_int(cypher_executor):
    cypher_executor.execute("CREATE (n:Person {name: 'John', age: 30})")
    result = cypher_executor.execute("MATCH (n) WHERE n.age = 30 RETURN n")
    assert len(result) == 1
    assert result[0]['properties'] == {'name': 'John', 'age': 30}