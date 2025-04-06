import json
import networkx as nx

# Load the JSON data from the file
with open('teststationData.json', 'r') as file:
    data = json.load(file)

# Create a directed graph
G = nx.DiGraph()

# Iterate over each node in the data
for node_id, node_info in data.items():
    node_id = int(node_id)
    G.add_node(node_id)

    # Add intra-system edges (cost = 1)
    for neighbor in node_info.get('intraSystemNeighbors', []):
        G.add_edge(node_id, neighbor, weight=1)

    # Add inter-system edges (cost = 2)
    for neighbor in node_info.get('interSystemNeighbors', []):
        G.add_edge(node_id, neighbor, weight=2)

# Define source and target nodes
source = 60003466  # Example starting node
target = 60008494  # Example destination node

# Find the shortest path using Dijkstra's algorithm
try:
    path = nx.dijkstra_path(G, source, target, weight='weight')
    total_cost = nx.dijkstra_path_length(G, source, target, weight='weight')
    print(f"Optimal path from {source} to {target}: {path}")
    print(f"Total travel cost: {total_cost}")
except nx.NetworkXNoPath:
    print(f"No path exists between {source} and {target}")
