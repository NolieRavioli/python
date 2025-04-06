import json
from collections import defaultdict, deque
import heapq

# -----------------------------
# Configuration
# -----------------------------
BUDGET = 200_000_000
LOCATION = 30001132 # 863P-X (30001132)
DESTINATION = None  # Set to a system id MJ-5F9 (30005133) to require a specific destination; None to ignore destination.
maxJumps = 70   # now includes stargate hops + station visits

MARKET_FILE = "marketOrders.json"
GRAPH_FILE = "system_graph.json"
OWNED_BPS_FILE = "list2.txt"

# -----------------------------
# 1) Load system graph
# -----------------------------
with open(GRAPH_FILE, "r", encoding="utf-8") as f:
    system_graph = json.load(f)

# Convert keys to strings
for k in list(system_graph.keys()):
    neighbors = system_graph[k]
    system_graph[k] = [str(n) for n in neighbors if n is not None]

def dijkstra(source, dest):
    """
    Returns the minimum number of jumps (edge count) required to travel from source to dest.
    Assumes each edge (stargate jump) has a cost of 1.
    If no route exists, returns float('inf').
    """
    pq = [(0, source)]
    visited = set()
    while pq:
        cost, node = heapq.heappop(pq)
        if node == dest:
            return cost
        if node in visited:
            continue
        visited.add(node)
        for neighbor in system_graph.get(node, []):
            if neighbor not in visited:
                heapq.heappush(pq, (cost + 1, neighbor))
    return float('inf')

# -----------------------------
# Compute set of systems reachable within maxJumps stargate hops
# -----------------------------
startSys = str(LOCATION)
maxJumpSystems = set()
bfs_queue = deque([(startSys, 0)])
while bfs_queue:
    current, jumps = bfs_queue.popleft()
    if jumps > maxJumps:
        continue
    if current in maxJumpSystems:
        continue
    if DESTINATION:
        if jumps + dijkstra(current, str(DESTINATION)) > maxJumps:
            continue
    maxJumpSystems.add(current)
    for neighbor in system_graph.get(current, []):
        if neighbor not in maxJumpSystems:
            bfs_queue.append((neighbor, jumps + 1))

# -----------------------------
# 2) Load owned BPs
# -----------------------------
with open(OWNED_BPS_FILE, "r", encoding="utf-8") as f:
    owned_bps = set(line.split('\t')[0].strip() for line in f)

# -----------------------------
# 3) Parse market data, restricting to systems within maxJumpSystems
# -----------------------------
with open(MARKET_FILE, "r", encoding="utf-8") as f:
    market_data = json.load(f)

stations_in_system = defaultdict(list)
for locID, items in market_data.items():
    if "systemId" not in items or "stationName" not in items:
        continue
    sys_id_str = str(items["systemId"])
    station_name = items["stationName"]

    # Only process orders if system is reachable within maxJumps
    if sys_id_str not in maxJumpSystems:
        continue

    bpo_list = []
    for key, order_info in items.items():
        if not key.isdigit():
            continue
        bp_name = order_info["itemName"]
        price = order_info["price"]
        if bp_name in owned_bps: continue
        #if "Capital " in bp_name: continue
        bpo_list.append((price, bp_name))
    if bpo_list:
        bpo_list.sort(key=lambda x: x[0])
        stations_in_system[sys_id_str].append({
            "locID": locID,
            "stationName": station_name,
            "bpoList": bpo_list
        })

# -----------------------------
# 3.1) Compute global cheapest BPOs
# -----------------------------
global_cheapest_bpos = {}
for sys_id, station_list in stations_in_system.items():
    for station in station_list:
        for price, bp_name in station["bpoList"]:
            if bp_name not in global_cheapest_bpos or price < global_cheapest_bpos[bp_name]:
                global_cheapest_bpos[bp_name] = price

# -----------------------------
# 3.2) Build allowed set of BPO itemIds
# -----------------------------
sorted_bps = sorted(global_cheapest_bpos.items(), key=lambda x: x[1])
allowed_set = set()
cumulative = 0
for bp_name, price in sorted_bps:
    if cumulative + price > BUDGET:
        break
    allowed_set.add(bp_name)
    cumulative += price

# -----------------------------
# 3.3) Filter each station's order list to only include orders for allowed BPOs,
#       and only if they match the global cheapest price.
# -----------------------------
for sys_id, station_list in stations_in_system.items():
    for station in station_list:
        station["bpoList"] = [
            (price, bp_name)
            for (price, bp_name) in station["bpoList"]
            if bp_name in allowed_set and price == global_cheapest_bpos[bp_name]
        ]

# -----------------------------
# 4) Buy function (only purchases allowed BPOs)
# -----------------------------
def buy_bpos_in_all_stations(systemId, budget, purchasedSet):
    stationPurchases = []
    total_bought = 0
    newBudget = budget
    updatedPurchased = set(purchasedSet)
    stationsVisited = 0

    for station_info in stations_in_system.get(systemId, []):
        stName = station_info["stationName"]
        bpo_list = station_info["bpoList"]
        purchased_here = []
        spent = 0
        for (bp_price, bp_name) in bpo_list:
            if bp_name in updatedPurchased:
                continue
            if bp_name not in allowed_set:
                continue
            if spent + bp_price > newBudget:
                break
            spent += bp_price
            purchased_here.append(bp_name)
            updatedPurchased.add(bp_name)
        if purchased_here:
            total_bought += len(purchased_here)
            newBudget -= spent
            stationPurchases.append((stName, purchased_here))
            stationsVisited += 1
    return total_bought, newBudget, stationPurchases, updatedPurchased, stationsVisited

# --------------------------------------------------------------
# 5) BFS with multi-criteria pruning (optimizing allowed BPOs per jump)
# --------------------------------------------------------------
visited = {}
queue = deque()

startSys = str(LOCATION)
bCount, newBudget, stPurchases, purchasedSet, stVisited = buy_bpos_in_all_stations(
    startSys, BUDGET, set()
)
start_jumps = stVisited
start_state = (
    startSys,         # current system
    newBudget,        # budget left
    start_jumps,      # jumps so far
    len(purchasedSet),# distinct allowed items purchased so far
    [(startSys, stPurchases)],  # path so far (list of (system, station purchase details))
    purchasedSet      # purchased allowed items
)
visited[(startSys, newBudget, frozenset(purchasedSet))] = (len(purchasedSet), start_jumps)
queue.append(start_state)

# Track best result using the ratio "Allowed BPOs per Jump"
best_path = None
best_ratio = 0.0
best_jumps = 9999999
best_distinct = 0

while queue:
    currentSystem, budgetLeft, jumpsSoFar, distinctCount, pathSoFar, purchasedSetSoFar = queue.popleft()
    
    # If DESTINATION is set, consider a state valid if currentSystem matches.
    # If DESTINATION is None, every state is a candidate.
    if (DESTINATION is not None and currentSystem == str(DESTINATION)) or (DESTINATION is None):
        # Calculate ratio; avoid division by zero.
        ratio = distinctCount / jumpsSoFar if jumpsSoFar > 0 else 0
        if ratio > best_ratio or (abs(ratio - best_ratio) < 1e-9 and jumpsSoFar < best_jumps):
            best_ratio = ratio
            best_distinct = distinctCount
            best_jumps = jumpsSoFar
            best_path = pathSoFar
            price = BUDGET - budgetLeft
    
    if jumpsSoFar >= maxJumps:
        continue
    if currentSystem not in system_graph:
        continue

    for neighborSys in system_graph[currentSystem]:
        baseJumps = jumpsSoFar + 1  # one stargate jump
        bBought, newBgt, stPurch, newPurchSet, stVisitedCount = buy_bpos_in_all_stations(
            neighborSys, budgetLeft, purchasedSetSoFar
        )
        total_jumps = baseJumps + stVisitedCount
        if total_jumps > maxJumps:
            continue
        new_distinct = len(newPurchSet)
        key = (neighborSys, newBgt, frozenset(newPurchSet))
        old_record = visited.get(key, (-1, 9999999))
        old_distinct, old_jumps = old_record
        if not (new_distinct > old_distinct or (new_distinct == old_distinct and total_jumps < old_jumps)):
            continue
        visited[key] = (new_distinct, total_jumps)
        new_path = pathSoFar + [(neighborSys, stPurch)]
        new_state = (
            neighborSys,
            newBgt,
            total_jumps,
            new_distinct,
            new_path,
            newPurchSet
        )
        queue.append(new_state)

# -----------------------------
# 6) Print results
# -----------------------------
if best_path is None:
    if DESTINATION is None:
        print(f"No route found from {LOCATION} within {maxJumps} jumps that collects allowed BPOs.")
    else:
        print(f"No route found from {LOCATION} to {DESTINATION} within {maxJumps} jumps that collects allowed BPOs.")
else:
    print("=== Best Route Found ===")
    print(f"Start: {LOCATION}" + (f", Destination: {DESTINATION}" if DESTINATION is not None else ""))
    print(f"Jumps: {best_jumps}")
    print(f"Distinct Allowed BPOs Purchased: {best_distinct}")
    print(f"Allowed BPOs per Jump: {best_ratio:.2f}")
    print(f"Total Price: {price}")
    print()
    
    purchasesBPs = set()
    for sys_id, station_list in best_path:
        station_purchases = []
        for (stName, bpsBought) in station_list:
            if bpsBought:
                station_purchases.append((stName, bpsBought))
        if station_purchases:
            for (stName, bpsBought) in station_purchases:
                for bp in bpsBought:
                    purchasesBPs.add(bp)
    
    if len(purchasesBPs) >= 100:
        stop_counter = 1
        for sys_id, station_list in best_path:
            station_purchases = []
            for (stName, bpsBought) in station_list:
                if bpsBought:
                    station_purchases.append((stName, bpsBought))
            if station_purchases:
                print(f"Stop {stop_counter}: System {sys_id}")
                for (stName, bpsBought) in station_purchases:
                    print(f"  - Station: {stName}")
                    for bp in bpsBought:
                        print(bp)
                    print()
                print()
                stop_counter += 1
    else:
        stop_counter = 1
        for sys_id, station_list in best_path:
            station_purchases = []
            for (stName, bpsBought) in station_list:
                if bpsBought:
                    station_purchases.append((stName, bpsBought))
            if station_purchases:
                print(f"Stop {stop_counter}: System {sys_id}")
                for (stName, bpsBought) in station_purchases:
                    print(f"  - Station: {stName}")
                stop_counter += 1
        print("\nShopping List:")
        for bp in purchasesBPs:
            print(bp)
