# cxdb/core.py

import pandas as pd

class CXDB:
    def __init__(self):
        self.nodes = pd.DataFrame(columns=['id', 'name', 'type', 'properties'])
        self.edges = pd.DataFrame(columns=['source_id', 'target_id', 'relationship', 'properties'])
        self.next_node_id = 1
        self.node_names = set()

    def add_node(self, name, type, properties=None):
        if name in self.node_names:
            raise ValueError("Node name must be unique")
        if properties is None:
            properties = {}
        node_id = int(self.next_node_id)
        self.next_node_id += 1
        new_node = pd.DataFrame([[node_id, name, type, properties]], columns=self.nodes.columns)
        self.nodes = pd.concat([self.nodes, new_node], ignore_index=True)
        self.node_names.add(name)
        return node_id

    def get_node(self, node_id):
        node = self.nodes[self.nodes['id'] == node_id]
        if node.empty:
            return None
        return node.iloc[0].to_dict()

    def add_edge(self, source_id, target_id, relationship, properties=None):
        if properties is None:
            properties = {}
        new_edge = pd.DataFrame([[int(source_id), int(target_id), relationship, properties]], 
                                columns=self.edges.columns)
        self.edges = pd.concat([self.edges, new_edge], ignore_index=True)

    def get_edge(self, source_id, target_id, relationship):
        edge = self.edges[(self.edges['source_id'] == source_id) & 
                          (self.edges['target_id'] == target_id) & 
                          (self.edges['relationship'] == relationship)]
        if edge.empty:
            return None
        return edge.iloc[0].to_dict()

    def update_node(self, node_id, name=None, type=None, properties=None):
        node_index = self.nodes[self.nodes['id'] == node_id].index
        
        if node_index.empty:
            raise ValueError("Node not found")
        
        if name:
            if name in self.node_names:
                raise ValueError("Node name must be unique")
            old_name = self.nodes.at[node_index[0], 'name']
            self.node_names.remove(old_name)
            self.nodes.at[node_index[0], 'name'] = name
            self.node_names.add(name)
        
        if type:
            self.nodes.at[node_index[0], 'type'] = type
        
        if properties:
            current_properties = self.nodes.at[node_index[0], 'properties']
            for key, value in properties.items():
                if value is None:
                    current_properties.pop(key, None)
                else:
                    current_properties[key] = value
            self.nodes.at[node_index[0], 'properties'] = current_properties
        
        return node_id

    def update_edge(self, source_id, target_id, relationship, properties=None):
        edge_index = self.edges[(self.edges['source_id'] == source_id) & 
                                (self.edges['target_id'] == target_id) & 
                                (self.edges['relationship'] == relationship)].index
        
        if edge_index.empty:
            raise ValueError("Edge not found")

        if properties:
            current_properties = self.edges.at[edge_index[0], 'properties']
            for key, value in properties.items():
                if value is None:
                    current_properties.pop(key, None)
                else:
                    current_properties[key] = value
            self.edges.at[edge_index[0], 'properties'] = current_properties

    def delete_node(self, node_id):
        node = self.nodes[self.nodes['id'] == node_id]
        if node.empty:
            raise ValueError("Node not found")
        
        node_name = node.iloc[0]['name']
        self.node_names.remove(node_name)
        self.nodes = self.nodes[self.nodes['id'] != node_id]
        self.edges = self.edges[(self.edges['source_id'] != node_id) & (self.edges['target_id'] != node_id)]

    def delete_edge(self, source_id, target_id, relationship):
        edge = self.edges[(self.edges['source_id'] == source_id) & 
                          (self.edges['target_id'] == target_id) & 
                          (self.edges['relationship'] == relationship)]
        if edge.empty:
            raise ValueError("Edge not found")
        
        self.edges = self.edges[~((self.edges['source_id'] == source_id) & 
                                  (self.edges['target_id'] == target_id) & 
                                  (self.edges['relationship'] == relationship))]
        
    def clear(self):
        """
        Clear all data from the CXDB instance, resetting it to its initial state.
        """
        self.nodes = pd.DataFrame(columns=['id', 'name', 'type', 'properties'])
        self.edges = pd.DataFrame(columns=['source_id', 'target_id', 'relationship', 'properties'])
        self.next_node_id = 1
        self.node_names.clear()