# cxdb
CXDB is a lightweight, in-memory graph database that supports basic Cypher operations. It is backed by CX2, either as files or stored on NDEx.

The purpose of CX is to facilitate applications' use of knowledge graphs without configuring a database server. Notably, the application can easily have multiple separate knowledge graphs with different schemas in memory simultaneously. The use of NDEx for knowledge graph storage enables easy data sharing with other users, publication of knowledge graphs with stable DOIs, and interoperability with the Cytoscape ecosystem of network tools.

AI agents are a driving use case for CXDB. It is intended to facilitate methods such as GraphRAG or structured representation of goals, plans, actions, agent history, and inter-agent communications.

