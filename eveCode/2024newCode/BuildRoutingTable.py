import json
import networkx as nx

def build_graph(systems):
    """
    Build a graph from the systems data, ensuring all nodes are added even if they have no neighbors.
    """
    graph = nx.Graph()
    for system_id, data in systems.items():
        neighbors = data['neighbors']
        if neighbors:
            for neighbor in neighbors:
                graph.add_edge(str(system_id), str(neighbor))
    return graph

def compute_routing_table(graph, systems):
    """
    Compute the shortest path routing table using Dijkstra's algorithm.
    Handle isolated nodes and missing paths gracefully.
    """
    total = len(systems)
    routing_table = {}
    count = 0

    for system in systems:
        system_str = str(system)
        routing_table[system_str] = {}
        if system_str in graph:  # Check if the node exists in the graph
            distances = nx.single_source_dijkstra_path_length(graph, source=system_str)
            for target, distance in distances.items():
                if system_str != target:
                    routing_table[system_str][target] = distance
        else:
            # If the node is isolated, mark all distances as infinity
            for target in systems:
                if system != target:
                    routing_table[system_str][str(target)] = float('inf')

        count += 1
        if count % (total // 1000) == 0 or count == total:
            print(f'{100 * count / total:.2f}% done building')

    return routing_table

def main():
    # Load systems data
    with open('systemData.json', 'r') as f:
        systems = json.load(f)

    # Build the graph
    graph = build_graph(systems)

    # Compute the routing table
    routing_table = compute_routing_table(graph, systems)

    # Save the routing table
    with open('routingTable.json', 'w') as f:
        json.dump(routing_table, f)

if __name__ == "__main__":
    main()
