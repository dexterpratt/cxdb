# test_core.py

import pytest
from cxdb.core import CXDB

def test_cxdb_initialization():
    db = CXDB()
    assert db.nodes.empty
    assert db.edges.empty
    assert db.next_node_id == 1
    assert len(db.node_names) == 0

def test_add_node():
    db = CXDB()
    node_id = db.add_node("Node1", "TestType", {"key": "value"})
    assert not db.nodes.empty
    assert len(db.nodes) == 1
    assert db.nodes.iloc[0]['id'] == node_id
    assert db.nodes.iloc[0]['name'] == "Node1"
    assert db.nodes.iloc[0]['type'] == "TestType"
    assert db.nodes.iloc[0]['properties'] == {"key": "value"}
    assert "Node1" in db.node_names
    assert db.next_node_id == 2

def test_add_node_duplicate_name():
    db = CXDB()
    db.add_node("Node1", "TestType")
    with pytest.raises(ValueError, match="Node name must be unique"):
        db.add_node("Node1", "AnotherType")

def test_get_node():
    db = CXDB()
    node_id = db.add_node("Node1", "TestType", {"key": "value"})
    node = db.get_node(node_id)
    assert node is not None
    assert node['id'] == node_id
    assert node['name'] == "Node1"
    assert node['type'] == "TestType"
    assert node['properties'] == {"key": "value"}

def test_get_nonexistent_node():
    db = CXDB()
    assert db.get_node(999) is None

def test_add_edge():
    db = CXDB()
    node1_id = db.add_node("Node1", "TestType")
    node2_id = db.add_node("Node2", "TestType")
    db.add_edge(node1_id, node2_id, "TestRelation", {"key": "value"})
    assert not db.edges.empty
    assert len(db.edges) == 1
    edge = db.edges.iloc[0]
    assert edge['source_id'] == node1_id
    assert edge['target_id'] == node2_id
    assert edge['relationship'] == "TestRelation"
    assert edge['properties'] == {"key": "value"}

def test_get_edge():
    db = CXDB()
    node1_id = db.add_node("Node1", "TestType")
    node2_id = db.add_node("Node2", "TestType")
    db.add_edge(node1_id, node2_id, "TestRelation", {"key": "value"})
    edge = db.get_edge(node1_id, node2_id, "TestRelation")
    assert edge is not None
    assert edge['source_id'] == node1_id
    assert edge['target_id'] == node2_id
    assert edge['relationship'] == "TestRelation"
    assert edge['properties'] == {"key": "value"}

def test_get_nonexistent_edge():
    db = CXDB()
    node1_id = db.add_node("Node1", "TestType")
    node2_id = db.add_node("Node2", "TestType")
    assert db.get_edge(node1_id, node2_id, "NonexistentRelation") is None

def test_update_node():
    db = CXDB()
    node_id = db.add_node("Node1", "TestType", {"key": "value"})
    db.update_node(node_id, name="UpdatedNode", type="NewType", properties={"new_key": "new_value"})
    updated_node = db.get_node(node_id)
    assert updated_node['name'] == "UpdatedNode"
    assert updated_node['type'] == "NewType"
    assert updated_node['properties'] == {"key": "value", "new_key": "new_value"}
    assert "UpdatedNode" in db.node_names
    assert "Node1" not in db.node_names

def test_update_nonexistent_node():
    db = CXDB()
    with pytest.raises(ValueError, match="Node not found"):
        db.update_node(999, name="UpdatedNode")

def test_update_node_duplicate_name():
    db = CXDB()
    db.add_node("Node1", "TestType")
    node2_id = db.add_node("Node2", "TestType")
    with pytest.raises(ValueError, match="Node name must be unique"):
        db.update_node(node2_id, name="Node1")

def test_update_edge():
    db = CXDB()
    node1_id = db.add_node("Node1", "TestType")
    node2_id = db.add_node("Node2", "TestType")
    db.add_edge(node1_id, node2_id, "TestRelation", {"key": "value"})
    db.update_edge(node1_id, node2_id, "TestRelation", {"new_key": "new_value"})
    updated_edge = db.get_edge(node1_id, node2_id, "TestRelation")
    assert updated_edge['properties'] == {"key": "value", "new_key": "new_value"}

def test_update_nonexistent_edge():
    db = CXDB()
    node1_id = db.add_node("Node1", "TestType")
    node2_id = db.add_node("Node2", "TestType")
    with pytest.raises(ValueError, match="Edge not found"):
        db.update_edge(node1_id, node2_id, "NonexistentRelation", {"key": "value"})

def test_delete_node():
    db = CXDB()
    node1_id = db.add_node("Node1", "TestType")
    node2_id = db.add_node("Node2", "TestType")
    db.add_edge(node1_id, node2_id, "TestRelation")
    db.delete_node(node1_id)
    assert db.get_node(node1_id) is None
    assert "Node1" not in db.node_names
    assert db.edges.empty

def test_delete_nonexistent_node():
    db = CXDB()
    with pytest.raises(ValueError, match="Node not found"):
        db.delete_node(999)

def test_delete_edge():
    db = CXDB()
    node1_id = db.add_node("Node1", "TestType")
    node2_id = db.add_node("Node2", "TestType")
    db.add_edge(node1_id, node2_id, "TestRelation")
    db.delete_edge(node1_id, node2_id, "TestRelation")
    assert db.get_edge(node1_id, node2_id, "TestRelation") is None
    assert db.edges.empty

def test_delete_nonexistent_edge():
    db = CXDB()
    node1_id = db.add_node("Node1", "TestType")
    node2_id = db.add_node("Node2", "TestType")
    with pytest.raises(ValueError, match="Edge not found"):
        db.delete_edge(node1_id, node2_id, "NonexistentRelation")