import unittest
import os
from cxdb.core import CXDB
from cxdb.ndex import NDExConnector
from cxdb.utils import load_config
import pandas as pd

TEST_CONFIG_PATH = os.path.expanduser('~/cxdb/test_config.ini')

class TestNDExIntegration(unittest.TestCase):
    def setUp(self):
        self.cxdb = CXDB()
        self.ndex_connector = NDExConnector(self.cxdb, config_path=TEST_CONFIG_PATH)
        self.test_uuid = load_config('TEST', 'test_network_uuid', config_path=TEST_CONFIG_PATH)

    def test_import_from_ndex(self):
        # Import the network from NDEx
        self.ndex_connector.from_ndex(self.test_uuid)

        # Check that nodes and edges were imported
        self.assertGreater(len(self.cxdb.nodes), 0)
        self.assertGreater(len(self.cxdb.edges), 0)

    def test_node_property_vocabulary(self):
        self.ndex_connector.from_ndex(self.test_uuid)
        node_properties = self.get_property_vocabulary(self.cxdb.nodes)
        
        # Print node property vocabulary
        print("Node Property Vocabulary:")
        for prop, count in node_properties.items():
            print(f"{prop}: {count}")

        # Assert that some expected properties are present
        self.assertIn('name', node_properties)
        self.assertIn('type', node_properties)

    def test_edge_property_vocabulary(self):
        self.ndex_connector.from_ndex(self.test_uuid)
        edge_properties = self.get_property_vocabulary(self.cxdb.edges)
        
        # Print edge property vocabulary
        print("Edge Property Vocabulary:")
        for prop, count in edge_properties.items():
            print(f"{prop}: {count}")

        # Assert that some expected properties are present
        self.assertIn('relationship', edge_properties)

    def get_property_vocabulary(self, df):
        property_counts = {}
        for _, row in df.iterrows():
            properties = row['properties']
            for prop in properties.keys():
                if prop in property_counts:
                    property_counts[prop] += 1
                else:
                    property_counts[prop] = 1
        
        # Add built-in properties
        for column in df.columns:
            if column != 'properties':
                property_counts[column] = len(df)

        return dict(sorted(property_counts.items(), key=lambda x: x[1], reverse=True))

    def test_cypher_query_on_imported_data(self):
        self.ndex_connector.from_ndex(self.test_uuid)
        
        # Get the most common node type
        node_types = self.cxdb.nodes['type'].value_counts()
        if not node_types.empty:
            most_common_type = node_types.index[0]
        else:
            self.fail("No node types found in the imported data")

        # Example Cypher query to get all nodes of the most common type
        query = f"MATCH (n:{most_common_type}) RETURN n.name AS name"
        
        try:
            result = self.cxdb.execute_cypher(query)
            self.assertIsInstance(result, list)
            self.assertGreater(len(result), 0)  # Ensure we got at least one result
            for item in result:
                self.assertIn('name', item)
            print(f"Successfully queried {len(result)} nodes of type '{most_common_type}'")
        except Exception as e:
            self.fail(f"Cypher query execution failed: {str(e)}\nQuery: {query}")

    def test_basic_graph_structure(self):
        self.ndex_connector.from_ndex(self.test_uuid)
        
        print("\nBasic Graph Structure:")
        print(f"Number of nodes: {len(self.cxdb.nodes)}")
        print(f"Number of edges: {len(self.cxdb.edges)}")
        
        print("\nNode types:")
        print(self.cxdb.nodes['type'].value_counts())
        
        print("\nEdge types:")
        print(self.cxdb.edges['relationship'].value_counts())

if __name__ == '__main__':
    unittest.main()