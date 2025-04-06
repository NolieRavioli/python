import os
import json
import yaml
import heapq
import requests
from collections import deque

# Paths
SDE_UNIVERSE_PATH = r"C:\Users\nolan\Desktop\old m.2\Users\Nolan\Desktop\Eve Online Code\eve"
PRECOMPUTED_ROUTES_FILE = "precomputed_routes.json"
SYSTEM_GRAPH_FILE = "system_graph.json"  # <-- New file to store the system graph
START_SYSTEM_ID = 30005133  # MJ-5F9
JUMPGATE_FILE = "JUMPGATES.txt"

# Use faster CLoader if available
try:
    from yaml import CLoader as Loader
except ImportError:
    print('fallback on loader')
    from yaml import SafeLoader as Loader


def get_system_ids(system_names):
    """
    Given a list of solar system names, return a dictionary mapping names to their corresponding IDs using ESI.
    """
    url = "https://esi.evetech.net/latest/universe/ids/"
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=system_names, headers=headers)
    response.raise_for_status()
    data = response.json()
    
    return {item['name']: item['id'] for item in data.get('systems', [])}


def load_stargate_to_system_mapping():
    """
    Reads all solar system YAML files from the SDE to create a mapping of stargates to their corresponding solar systems.
    """
    stargate_to_system = {}
    for root, _, files in os.walk(SDE_UNIVERSE_PATH):
        for file in files:
            if file == "solarsystem.yaml":
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = yaml.load(f, Loader=Loader)
                        system_id = data.get("solarSystemID")
                        stargates = data.get("stargates", {})

                        for stargate_id in stargates:
                            stargate_to_system[int(stargate_id)] = system_id
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")
    return stargate_to_system


def load_solar_system_connections():
    """
    Reads all solar system YAML files from the SDE and builds a graph of system connections via stargates.
    """
    system_graph = {}
    stargate_to_system = load_stargate_to_system_mapping()
    for root, _, files in os.walk(SDE_UNIVERSE_PATH):
        for file in files:
            if file == "solarsystem.yaml":
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = yaml.load(f, Loader=Loader)
                        system_id = data.get("solarSystemID")
                        stargates = data.get("stargates", {})

                        if system_id and stargates:
                            if system_id not in system_graph:
                                system_graph[system_id] = []
                            for stargate in stargates.values():
                                destination_gate = stargate["destination"]
                                destination_system = stargate_to_system.get(destination_gate)
                                if destination_system:
                                    if destination_system not in system_graph:
                                        system_graph[destination_system] = []
                                    if destination_system not in system_graph[system_id]:
                                        system_graph[system_id].append(destination_system)
                                    if system_id not in system_graph[destination_system]:
                                        system_graph[destination_system].append(system_id)
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")
    return system_graph


def add_jump_gate_connections(system_graph):
    """
    Reads the jump gate connections from JUMPGATES.txt and adds them to the system graph.
    """
    with open(JUMPGATE_FILE, 'r') as file:
        jumpgates = [line.strip().split(',') for line in file.readlines()]

    # Collect all system names and map them to their IDs
    system_names = list(set([item for sublist in jumpgates for item in sublist]))
    system_id_map = get_system_ids(system_names)

    for system_a, system_b in jumpgates:
        system_a_id = system_id_map.get(system_a)
        system_b_id = system_id_map.get(system_b)
        if system_a_id and system_b_id:
            if system_a_id not in system_graph:
                system_graph[system_a_id] = []
            if system_b_id not in system_graph:
                system_graph[system_b_id] = []
            if system_b_id not in system_graph[system_a_id]:
                system_graph[system_a_id].append(system_b_id)
            if system_a_id not in system_graph[system_b_id]:
                system_graph[system_b_id].append(system_a_id)
        else:
            print(f"Warning: Could not find ID for {system_a} or {system_b}")


def dijkstra(graph, start_system):
    """
    Computes the shortest number of jumps from start_system to all other systems using Dijkstra’s Algorithm.
    """
    distances = {system: float("inf") for system in graph}
    distances[start_system] = 0
    priority_queue = [(0, start_system)]
    
    while priority_queue:
        current_distance, current_system = heapq.heappop(priority_queue)
        
        # If our current distance exceeds the recorded distance, skip
        if current_distance > distances[current_system]:
            continue
        
        for neighbor in graph.get(current_system, []):
            distance = current_distance + 1  # Each jump costs 1
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(priority_queue, (distance, neighbor))
    
    # Remove unreachable systems (those that remain inf)
    return {sys: jumps for sys, jumps in distances.items() if jumps != float("inf")}


def precompute_shortest_routes():
    """
    Loads solar system connections, calculates shortest routes from START_SYSTEM_ID, 
    saves them to a JSON file, and also exports the system graph to a JSON file.
    """
    print("Loading solar system connections from SDE...")
    system_graph = load_solar_system_connections()
    
    print("Adding jump gate connections...")
    add_jump_gate_connections(system_graph)
    
    # Optional: Save system graph to a JSON file
    print(f"Saving system graph to {SYSTEM_GRAPH_FILE}...")
    with open(SYSTEM_GRAPH_FILE, "w", encoding="utf-8") as f:
        json.dump(system_graph, f, indent=2)
    
    print(f"Starting Dijkstra’s shortest path calculation from {START_SYSTEM_ID}...")
    jump_distances = dijkstra(system_graph, START_SYSTEM_ID)
    
    print(f"Saving precomputed shortest paths to {PRECOMPUTED_ROUTES_FILE}...")
    with open(PRECOMPUTED_ROUTES_FILE, "w", encoding="utf-8") as f:
        json.dump(jump_distances, f, indent=2)
    
    print(f"Precomputed shortest paths saved! ({len(jump_distances)} systems mapped)")
    print(f"System graph saved to {SYSTEM_GRAPH_FILE}!")


def get_shortest_route(destination_system_id):
    """
    Loads the precomputed shortest path JSON file and retrieves the jump count for a given system.
    """
    if not hasattr(get_shortest_route, "cache"):
        print("Loading precomputed routes from file...")
        with open(PRECOMPUTED_ROUTES_FILE, "r", encoding="utf-8") as f:
            get_shortest_route.cache = json.load(f)
        print("Precomputed routes loaded.")
    return get_shortest_route.cache.get(str(destination_system_id), None)


if __name__ == "__main__":
    precompute_shortest_routes()
