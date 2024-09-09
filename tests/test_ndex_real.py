# tests/test_ndex_real.py

import pytest
import os
from cxdb.core import CXDB
from cxdb.ndex import NDExConnector
from cxdb.utils import load_config
import ndex2.client as nc2

TEST_CONFIG_PATH = os.path.expanduser('~/cxdb/test_config.ini')

@pytest.fixture
def cxdb():
    db = CXDB()
    db.add_node("Node1", "Type1", {"prop1": "value1"})
    db.add_node("Node2", "Type2", {"prop2": "value2"})
    db.add_edge(1, 2, "Relation1", {"edge_prop": "edge_value"})
    return db

@pytest.fixture
def ndex_connector(cxdb):
    connector = NDExConnector(cxdb, config_path=TEST_CONFIG_PATH)
    connector.ndex = nc2.Ndex2(connector.server, connector.username, connector.password)
    return connector

def test_to_cx2(ndex_connector):
    cx2_network = ndex_connector.to_cx2()
    assert len(cx2_network.get_nodes()) == 2
    assert len(cx2_network.get_edges()) == 1

def test_upload_and_download(ndex_connector):
    # Upload the network
    network_name = "CXDB Test Network"
    network_description = "This is a test network for CXDB"
    uuid = ndex_connector.to_ndex(network_name, network_description)
    
    assert uuid is not None
    client_resp = ndex_connector.ndex.get_network_as_cx2_stream(uuid)
    assert client_resp.status_code == 200
    
    # Clear the local CXDB
    ndex_connector.cxdb.clear()
    assert len(ndex_connector.cxdb.nodes) == 0
    assert len(ndex_connector.cxdb.edges) == 0
    
    # Download the network
    ndex_connector.from_ndex(uuid)
    
    # Verify the downloaded network
    assert len(ndex_connector.cxdb.nodes) == 2
    assert len(ndex_connector.cxdb.edges) == 1
    
    # Verify node properties
    node1 = ndex_connector.cxdb.get_node(1)
    assert node1['name'] == "Node1"
    assert node1['type'] == "Type1"
    assert node1['properties']['prop1'] == "value1"
    
    # Verify edge properties
    edge = ndex_connector.cxdb.get_edge(1, 2, "Relation1")
    assert edge is not None
    assert edge['properties']['edge_prop'] == "edge_value"
    
    # Clean up: delete the test network from NDEx
    ndex_connector.ndex.delete_network(uuid)

def test_update_existing_network(ndex_connector):
    # Create and upload an initial network
    initial_name = "CXDB Initial Test Network"
    uuid = ndex_connector.to_ndex(initial_name)
    
    # Modify the local network
    ndex_connector.cxdb.add_node("Node3", "Type3", {"prop3": "value3"})
    ndex_connector.cxdb.add_edge(2, 3, "Relation2")
    
    # Update the network on NDEx
    updated_name = "CXDB Updated Test Network"
    ndex_connector.to_ndex(updated_name)
    
    # Download the updated network to a new CXDB instance
    new_cxdb = CXDB()
    new_connector = NDExConnector(new_cxdb, config_path=TEST_CONFIG_PATH)
    new_connector.from_ndex(uuid)
    
    # Verify the updates
    assert len(new_connector.cxdb.nodes) == 3
    assert len(new_connector.cxdb.edges) == 2
    assert new_connector.cxdb.get_node(3)['name'] == "Node3"
    
    # Clean up
    ndex_connector.ndex.delete_network(uuid)

if __name__ == "__main__":
    pytest.main([__file__])