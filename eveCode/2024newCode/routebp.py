import json
import random
from collections import defaultdict
from multiprocessing import Pool

# Load JSON data
with open('bp.json', 'r') as f:
    blueprints = json.load(f)

with open('systemData.json', 'r') as f:
    systems = json.load(f)

with open('routingTable.json', 'r') as f:
    routingTable = json.load(f)
print('Loaded tables')

# Map systems to their attributes (itemIDs)
system_to_items = {str(system_id): set() for system_id in systems.keys()}
for item_id, details in blueprints.items():
    if details:
        for system in details[1]:  # List of systems where the item is available
            if str(system) in system_to_items.keys():
                system_to_items[str(system)].add(item_id)
for system in list(system_to_items.keys()):
    if not system_to_items[system]:
        system_to_items.pop(system)
print(f"Mapped systems to items: {len(system_to_items)} systems")

# Filter systems to only include those with neighbors
valid_systems = {system_id for system_id, data in systems.items() if data.get('neighbors')}

# Adjust system_to_items to only include valid systems
system_to_items = {system: items for system, items in system_to_items.items() if system in valid_systems}
print(f'validated {len(system_to_items)} systems for ant usage')

temp = routingTable
routingTable = {}
for system in temp:
    if system in system_to_items.keys():
        routingTable[system] = temp[system]

# Starting system
start_system = "30005133"  # MJ-5F9

# Required categories
required_items = set(i for i in blueprints.keys() if blueprints[i] is not None)  # All itemIDs to collect
print(f"Required items to collect: {len(required_items)} items")

# Parameters
num_ants = 1
iterations = 1
alpha = 1.0  # Influence of pheromone
beta = 2.0   # Influence of heuristic information (distance)
evaporation_rate = 0.5
pheromone_deposit = 100.0
num_processes = 1  # Adjust based on your CPU cores

# Initialize pheromones based on inverse distances
pheromones = {
    system: {neighbor: (1.0 / routingTable[system][neighbor]) if routingTable[system][neighbor] != float('inf') else 0.0
             for neighbor in routingTable[system]}
    for system in routingTable
}
print("Initialized pheromones with inverse distances.")

# Helper function to choose the next node
def choose_next_node(current_node, unvisited_nodes, pheromones, distances, alpha, beta):
    probabilities = []
    total = 0

    for node in unvisited_nodes:
        # Ensure the node is valid and connected
        if node in distances.get(current_node, {}):
            pheromone = pheromones[current_node][node] ** alpha
            distance = distances[current_node][node]
            heuristic = (1.0 / distance) ** beta if distance > 0 else 0
            prob = pheromone * heuristic
            probabilities.append((node, prob))
            total += prob

    if probabilities:
        probabilities = [(node, prob / total if total > 0 else 0) for node, prob in probabilities]
        nodes, probs = zip(*probabilities)
        chosen_node = random.choices(nodes, weights=probs, k=1)[0]
        print(f"Ant at {current_node}: chose {chosen_node}")
        return chosen_node
    else:
        print(f"Ant at {current_node}: no valid nodes available")
        return None

# Worker function for multiprocessing
def process_ants(args):
    print(f"Starting process_ants for {args[-1]} ants")
    start_system, required_items, system_to_items, pheromones, distances, alpha, beta, num_ants = args
    print(f"Distances loaded for process: {len(distances)} systems")
    routes = []
    distances_list = []

    for ant in range(num_ants):
        visited = set()
        current_node = start_system
        route = [current_node]
        total_distance = 0
        collected_items = set()

        while collected_items != required_items:
            unvisited_nodes = {node for node in system_to_items.keys() if node not in visited}
            if not unvisited_nodes:
                print(f"Ant {ant}: No unvisited nodes available")
                break

            next_node = choose_next_node(current_node, unvisited_nodes, pheromones, distances, alpha, beta)
            if next_node is None:
                print(f"Ant {ant}: No valid next node found from {current_node}")
                break

            route.append(next_node)
            visited.add(next_node)
            collected_items |= system_to_items[next_node]
            total_distance += distances[current_node].get(next_node, float('inf'))
            current_node = next_node

        # Return to start
        if start_system in distances[current_node]:
            route.append(start_system)
            total_distance += distances[current_node][start_system]

        routes.append(route)
        distances_list.append(total_distance)

        print(f"Ant {ant}: Distance = {total_distance}, Route length = {len(route)}")

    return routes, distances_list

# Ant colony optimization with multiprocessing
def ant_colony_optimization(start_system, required_items, system_to_items, routingTable, num_ants, iterations):
    distances = routingTable
    best_route = None
    best_distance = float('inf')

    for iteration in range(iterations):
        print(f"Starting iteration {iteration + 1}/{iterations}")
        with Pool(processes=num_processes) as pool:
            chunk_size = num_ants // num_processes
            args = [
                (start_system, required_items, system_to_items, pheromones, distances, alpha, beta, chunk_size)
                for _ in range(num_processes)
            ]
            print('check')
            results = pool.map(process_ants, args)

        # Combine results
        all_routes = []
        all_distances = []
        for routes, distances_list in results:
            all_routes.extend(routes)
            all_distances.extend(distances_list)

        # Update best route
        for route, distance in zip(all_routes, all_distances):
            if distance < best_distance:
                best_distance = distance
                best_route = route

        print(f"Iteration {iteration + 1}: Best distance so far = {best_distance}")

        # Update pheromones
        for route, distance in zip(all_routes, all_distances):
            if distance == float('inf'):
                continue
            pheromone_contribution = pheromone_deposit / distance
            for i in range(len(route) - 1):
                pheromones[route[i]][route[i + 1]] += pheromone_contribution

        print(f"Iteration {iteration + 1}: Pheromones updated")

    return best_route, best_distance

# Run the algorithm
best_route, best_distance = ant_colony_optimization(
    start_system=start_system,
    required_items=required_items,
    system_to_items=system_to_items,
    routingTable=routingTable,
    num_ants=num_ants,
    iterations=iterations
)

print("Best Route:", best_route)
print("Best Distance:", best_distance)
