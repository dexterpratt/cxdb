# cxdb/ndex.py

from ndex2.cx2 import CX2Network, RawCX2NetworkFactory
import ndex2.client as nc2
import json
import io
from .utils import load_config

class NDExConnector:
    def __init__(self, cxdb, config_path='~/cxdb/config.ini'):
        self.cxdb = cxdb
        self.cx2_network = None
        self.ndex_uuid = None
        
        # Load NDEx credentials
        self.server = load_config('NDEX', 'server', fallback='http://public.ndexbio.org', config_path=config_path)
        self.username = load_config('NDEX', 'username', config_path=config_path)
        self.password = load_config('NDEX', 'password', config_path=config_path)
        
        # Create NDEx client
        self.ndex = nc2.Ndex2(self.server, self.username, self.password)

    def to_cx2(self):
        if self.cx2_network is None:
            self.cx2_network = CX2Network()
        else:
            self.clear_cx2()

        # Add nodes from CXDB to CX2Network
        for _, node in self.cxdb.nodes.iterrows():
            node_attrs = {
                'name': node['name'],
                'type': node['type']
            }
            node_attrs.update(node['properties'])
            self.cx2_network.add_node(int(node['id']), node_attrs)

        # Add edges from CXDB to CX2Network
        for _, edge in self.cxdb.edges.iterrows():
            edge_attrs = {
                'interaction': edge['relationship']
            }
            edge_attrs.update(edge['properties'])
            edge_id = self.cx2_network.add_edge(source=int(edge['source_id']), target=int(edge['target_id']))
            self.cx2_network.update_edge(edge_id, edge_attrs)

        return self.cx2_network

    def to_ndex(self, name=None, description=None, visibility="PRIVATE"):
        cx2_network = self.to_cx2()
        if name is not None:
            cx2_network.add_network_attribute('name', name)
        if description is not None:
            cx2_network.add_network_attribute('description', description)
        
        if self.ndex_uuid:
            # Update existing network
            cx_stream = io.BytesIO(json.dumps(cx2_network.to_cx2()).encode('utf-8'))
            self.ndex.update_cx2_network(cx_stream, self.ndex_uuid)
        else:
            # Create new network
            url = self.ndex.save_new_cx2_network(cx2_network.to_cx2())
            self.ndex_uuid = url.split("/")[-1]


        # # Set visibility
        # if visibility == "PUBLIC":
        #     #self.ndex.make_network_public(self.ndex_uuid)
        #     self.ndex.set_network_system_properties(self.ndex_uuid, {"visibility": "PUBLIC"})
        # elif visibility == "PRIVATE":
        #     self.ndex.set_network_system_properties(self.ndex_uuid, {"visibility": "PRIVATE"})
        #     #self.ndex.make_network_private(self.ndex_uuid)
        
        return self.ndex_uuid

    def from_ndex(self, uuid):
        # Create CX2Network factory
        try:
            client_response = self.ndex.get_network_as_cx2_stream(uuid)
        except Exception as e:
            print(f"Error: {e}")
            return None
        factory = RawCX2NetworkFactory()
        cx2_network = factory.get_cx2network(json.loads(client_response.content))
        self.from_cx2(cx2_network)
        self.ndex_uuid = uuid
        return self.cxdb

    def from_cx2(self, cx2_network):
        self.cxdb.clear()
        self.cx2_network = cx2_network

        # Import nodes
        for node_id, node_data in cx2_network.get_nodes().items():
            node_attrs = node_data['v']
            name = node_attrs.pop('name', f"Node_{node_id}")
            node_type = node_attrs.pop('type', 'Default')
            self.cxdb.add_node(name, node_type, node_attrs)

        # Import edges
        for edge_id, edge_data in cx2_network.get_edges().items():
            edge = cx2_network.get_edge(edge_id)
            source_id = edge['s']
            target_id = edge['t']
            relationship = edge_data['v'].pop('interaction', 'interacts_with')
            self.cxdb.add_edge(source_id, target_id, relationship, edge_data['v'])

        return self.cxdb

    def clear_cx2(self):
        if self.cx2_network:
            for node_id in list(self.cx2_network.get_nodes()):
                self.cx2_network.remove_node(node_id)
            for edge_id in list(self.cx2_network.get_edges()):
                self.cx2_network.remove_edge(edge_id)