import json
import requests
import networkx as nx
import math

# Jita system ID (The Forge region, system Jita)
JITA_SYSTEM_ID = 30000142
start_input = JITA_SYSTEM_ID
activity = 'manufacturing'
minSec = 0.45
maxSec = 0.55

maxJumps = 25
maxShipKills = 0

# Load the JSON data from the file
with open('systemData.json', 'r') as file:
    systems = json.load(file)

highsecSystems = {}
for system in systems:
    if systems[system]['security'] >= 0.45:
        highsecSystems[system] = systems[system]

# Create a directed graph for routing (use original getRoute logic)
Gsystems = nx.DiGraph()
for node_id, node_info in highsecSystems.items():
    node_id = int(node_id)
    Gsystems.add_node(node_id)
    for neighbor in node_info.get('neighbors', []):
        Gsystems.add_edge(node_id, neighbor, weight=1)

def getRoute(source, target):
    if source == target:
        return 0
    try:
        total_cost = nx.dijkstra_path_length(Gsystems, source, target, weight='weight')
        return total_cost
    except nx.NetworkXNoPath:
        return float('inf')  # Return infinite cost if no path exists

# Fetch system kills data from ESI
def get_system_kills():
    url = "https://esi.evetech.net/latest/universe/system_kills/"
    response = requests.get(url)
    return {entry['system_id']: entry for entry in response.json()}

# Fetch system jumps data from ESI
def get_system_jumps():
    url = "https://esi.evetech.net/latest/universe/system_jumps/"
    response = requests.get(url)
    return {entry['system_id']: entry for entry in response.json()}

# Function to get all systems within n jumps from a given system using BFS-like search
def get_systems_within_n_jumps(start_system_id, max_jumps):
    visited = set([start_system_id])
    current_layer = {start_system_id}

    for _ in range(max_jumps):
        next_layer = set()
        for system_id in current_layer:
            if systems[str(system_id)]['security'] >= 0.45:
                neighbors = systems.get(str(system_id), {}).get('neighbors', [])
                for neighbor in neighbors:
                    if neighbor not in visited:
                        next_layer.add(neighbor)
                        visited.add(neighbor)
        current_layer = next_layer
        if not current_layer:
            break

    return visited

# Function to resolve system IDs to system names using ESI
def get_system_names(system_ids):
    BASE_URL = "https://esi.evetech.net/latest/universe/names/"
    headers = {"Content-Type": "application/json"}
    response = requests.post(BASE_URL, headers=headers, json=list(system_ids))
    return {item['id']: item['name'] for item in response.json()}

# Function to get sorted systems by manufacturing index within `n` jumps
def get_sorted_manufacturing_indices_near_jita(n_jumps, startSystem):
    systems_within_n_jumps = get_systems_within_n_jumps(startSystem, n_jumps)

    print(f'{len(systems_within_n_jumps)} systems within {n_jumps} jumps')
    
    # Fetch system names, system kills, and jumps for all systems within range
    system_names = get_system_names(systems_within_n_jumps)
    system_kills = get_system_kills()
    system_jumps = get_system_jumps()

    system_indices = []
    for system_id in systems_within_n_jumps:
        ave_index = 0
        for activtyCk in systems[str(system_id)]['cost_indices']:
            ave_index += systems[str(system_id)]['cost_indices'][activtyCk]
        ave_index /= 6
        manufacturing_index = systems[str(system_id)]['cost_indices'][activity] if systems[str(system_id)]['cost_indices'][activity] else 0
        jumps_from_jita = getRoute(startSystem, system_id)  # Calculate jumps from Jita
        
        # Get kill and jump data, defaulting to 0 if not found
        system_kill_data = system_kills.get(system_id, {'npc_kills': 0, 'ship_kills': 0, 'pod_kills': 0})
        system_jump_data = system_jumps.get(system_id, {'ship_jumps': 0})
        
        # Get system security
        system_security = systems[str(system_id)].get('security', 0)

        system_indices.append((
            system_id, 
            manufacturing_index,
            ave_index,
            jumps_from_jita, 
            system_kill_data['npc_kills'], 
            system_kill_data['ship_kills'], 
            system_kill_data['pod_kills'],
            system_jump_data['ship_jumps'],
            system_security
        ))

    # Sort by manufacturing index in ascending order
    sorted_system_indices = sorted(system_indices, key=lambda x: x[2])
    
    return sorted_system_indices, system_names

# Main function to get systems within `n` jumps from Jita and sort by manufacturing index
def main():
    start_input = input(f"Enter the starting system ID (default is Jita - {JITA_SYSTEM_ID}): ")
    start = int(start_input) if start_input else JITA_SYSTEM_ID
    n_jumps = int(input("Enter the number of jumps from start: "))
    sorted_systems, system_names = get_sorted_manufacturing_indices_near_jita(n_jumps, start)
    
    print("Systems sorted by manufacturing index (ascending):")
    for system_id, index, average, jumps, npc_kills, ship_kills, pod_kills, ship_jumps, security in sorted_systems:
        system_name = system_names.get(system_id, "Unknown")
        if ship_jumps <= maxJumps and ship_kills <= maxShipKills and (minSec <= security < maxSec):
            print(f"System: {system_name} (ID: {system_id}), ManIndex: {index:.4f},  average: {average:.4f}"
                  f" NPC Kills: {npc_kills}, Ship Kills: {ship_kills}, Pod Kills: {pod_kills}, "
                  f"Ship Jumps: {ship_jumps}, Jumps: {jumps+2}, Security: {security:.3f}")

if __name__ == "__main__":
    main()
