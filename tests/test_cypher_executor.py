# tests/test_cypher_executor.py

import pytest
from cxdb.core import CXDB

@pytest.fixture
def db():
    return CXDB()

def test_create_node(db):
    result = db.execute_cypher("CREATE (n:Person {name: 'Alice', age: 30})")
    assert isinstance(result, int)
    node = db.get_node(result)
    assert node['type'] == 'Person'
    assert node['properties'] == {'name': 'Alice', 'age': 30}

def test_match_query(db):
    db.execute_cypher("CREATE (n:Person {name: 'Alice', age: 30})")
    db.execute_cypher("CREATE (n:Person {name: 'Bob', age: 40})")
    
    result = db.execute_cypher("MATCH (n:Person) WHERE n.age = 30 RETURN n.name")
    assert len(result) == 1
    assert result[0]['n.name'] == 'Alice'

def test_delete_node(db):
    db.execute_cypher("CREATE (n:Person {name: 'Alice', age: 30})")
    db.execute_cypher("CREATE (n:Person {name: 'Bob', age: 40})")
    
    result = db.execute_cypher("DELETE (n:Person) WHERE n.name = 'Alice'")
    assert result == 1
    
    remaining = db.execute_cypher("MATCH (n:Person) RETURN n.name")
    assert len(remaining) == 1
    assert remaining[0]['n.name'] == 'Bob'

def test_complex_match_query(db):
    db.execute_cypher("CREATE (n:Person {name: 'Alice', age: 30, city: 'New York'})")
    db.execute_cypher("CREATE (n:Person {name: 'Bob', age: 40, city: 'Los Angeles'})")
    db.execute_cypher("CREATE (n:Person {name: 'Charlie', age: 35, city: 'New York'})")
    
    result = db.execute_cypher("MATCH (n:Person) WHERE n.age > 30 AND n.city = 'New York' RETURN n.name")
    assert len(result) == 1
    assert result[0]['n.name'] == 'Charlie'