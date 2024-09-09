import json
import ndex2
from ndex2.cx2 import RawCX2NetworkFactory, CX2NetworkXFactory

# Create NDEx2 python client
client = ndex2.client.Ndex2()

# Create CX2Network factory
factory = RawCX2NetworkFactory()


client_resp = client.get_network_as_cx2_stream('669f30a3-cee6-11ea-aaef-0ac135e8bacf')

# Convert downloaded network to CX2Network object
net_cx = factory.get_cx2network(json.loads(client_resp.content))

# Display information about network and output 1st 100 characters of CX2
print('Name: ' + net_cx.get_name())
print('Number of nodes: ' + str(len(net_cx.get_nodes())))
print('Number of nodes: ' + str(len(net_cx.get_edges())))
print(json.dumps(net_cx.to_cx2(), indent=2)[0:100])

# Create CX2NetworkXFactory
nxfac = CX2NetworkXFactory()
# Create Networkx network
g = nxfac.get_graph(net_cx)

print('Name: ' + str(g))
print('Number of nodes: ' + str(g.number_of_nodes()))
print('Number of edges: ' + str(g.number_of_edges()))
print('Network annotations: ' + str(g.graph))