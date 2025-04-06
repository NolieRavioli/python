import json
from collections import defaultdict, deque

# -----------------------------
# Configuration
# -----------------------------
BUDGET = 700_000_000
LOCATION = 30002060
DESTINATION = 30005133
maxJumps = 28   # Now includes stargate hops + station visits

MARKET_FILE = "marketOrders.json"
GRAPH_FILE = "system_graph.json"
OWNED_BPS_FILE = "list2.txt"

# -----------------------------
# 1) Load system graph
# -----------------------------
with open(GRAPH_FILE, "r", encoding="utf-8") as f:
    system_graph = json.load(f)

# Convert to string keys
for k in list(system_graph.keys()):
    neighbors = system_graph[k]
    system_graph[k] = [str(n) for n in neighbors if n is not None]

# -----------------------------
# 2) Load owned BPs
# -----------------------------
with open(OWNED_BPS_FILE, "r", encoding="utf-8") as f:
    owned_bps = set(line.split('\t')[0].strip() for line in f)

# -----------------------------
# 3) Parse market data
# -----------------------------
with open(MARKET_FILE, "r", encoding="utf-8") as f:
    market_data = json.load(f)

stations_in_system = defaultdict(list)

for locID, items in market_data.items():
    if "systemId" not in items or "stationName" not in items:
        continue
    sys_id_str = str(items["systemId"])
    station_name = items["stationName"]

    if sys_id_str in maxJumpSystems:

        bpo_list = []
        for key, order_info in items.items():
            if not key.isdigit():
                continue
            bp_name = order_info["itemName"]
            price = order_info["price"]

            # Example filter logic
            if bp_name in owned_bps:
                continue
            if "Capital " in bp_name:
                continue
            
            # Example further filter:
            lookFor = [
                'Structure Construction Parts',
                'Structure Hangar Array',
                'Structure Storage Bay',
                'Structure Laboratory',
                'Structure Factory',
                'Structure Repair Facility',
                'Structure Reprocessing Plant',
                'Structure Docking Bay',
                'Structure Electromagnetic Sensor',
                'Structure Market Network',
                'Structure Acceleration Coils',
                'Structure Medical Center',
                'Structure Office Center',
                'Astrahus',
                'Athanor',
                'Raitaru'
            ]
            #if not any(elem in bp_name for elem in lookFor): continue

            bpo_list.append((price, bp_name))

        if bpo_list:
            bpo_list.sort(key=lambda x: x[0])
            stations_in_system[sys_id_str].append({
                "locID": locID,
                "stationName": station_name,
                "bpoList": bpo_list
            })


# -----------------------------
# 4) Buy function
# -----------------------------
def buy_bpos_in_all_stations(systemId, budget, purchasedSet):
    """
    Buys as many BPOs as possible from each station in 'systemId', skipping
    BPO names already in purchasedSet.

    Returns:
      - total_bought (int): how many BPOs purchased
      - newBudget (int): leftover ISK
      - stationPurchases (list of (stationName, [bpName, ...]))
      - newPurchasedSet (set of bpName)
      - stationsVisited (int): how many distinct stations we actually purchased from
    """
    stationPurchases = []
    total_bought = 0
    newBudget = budget
    updatedPurchased = set(purchasedSet)
    visited_count = 0  # how many stations we actually buy from

    for station_info in stations_in_system[systemId]:
        stName = station_info["stationName"]
        bpo_list = station_info["bpoList"]

        purchased_here = []
        spent = 0
        for (bp_price, bp_name) in bpo_list:
            # skip if already purchased
            if bp_name in updatedPurchased:
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
            visited_count += 1  # we "visited" this station to buy

    return total_bought, newBudget, stationPurchases, updatedPurchased, visited_count

# --------------------------------------------------------------
# 5) BFS with multi-criteria pruning
# --------------------------------------------------------------
# visited[(system, budget, frozensetPurchased)] = (bestBposCount, fewestJumps)
visited = {}

queue = deque()

# -----------------------------
# Initialize BFS
#   Buy in the start system
# -----------------------------
startSys = str(LOCATION)
bCount, newBudget, stPurchases, purchasedSet, stVisited = buy_bpos_in_all_stations(
    startSys, BUDGET, set()
)

# We'll define "jumpsSoFar" to include station visits in the start system
start_jumps = 0 + stVisited

start_path = [(startSys, stPurchases)]
start_state = (
    startSys,         # currentSystem
    newBudget,        # budgetLeft
    start_jumps,      # jumpsSoFar
    bCount,           # bposBoughtSoFar
    start_path,       # pathSoFar
    purchasedSet      # purchasedSoFar
)

visited[(startSys, newBudget, frozenset(purchasedSet))] = (bCount, start_jumps)
queue.append(start_state)

# Track best
best_path = None
best_bpos = 0
best_jumps = 9999999
best_ratio = 0.0

# -----------------------------
# BFS loop
# -----------------------------
while queue:
    currentSystem, budgetLeft, jumpsSoFar, bposBoughtSoFar, pathSoFar, purchasedSetSoFar = queue.popleft()

    # If we've reached the destination, check ratio
    if currentSystem == str(DESTINATION):
        ratio = bposBoughtSoFar / max(1, jumpsSoFar)
        if ratio > best_ratio or (abs(ratio - best_ratio) < 1e-9 and jumpsSoFar < best_jumps):
            best_ratio = ratio
            best_jumps = jumpsSoFar
            best_bpos = bposBoughtSoFar
            best_path = pathSoFar
        continue

    # If we've hit our jump limit, skip
    if jumpsSoFar >= maxJumps:
        continue

    # If no neighbors, skip
    if currentSystem not in system_graph:
        continue

    # Explore neighbors
    for neighborSys in system_graph[currentSystem]:
        baseJumps = jumpsSoFar + 1  # stargate jump

        bBought, newBgt, stPurch, newPurchSet, stVisitedCount = buy_bpos_in_all_stations(
            neighborSys, budgetLeft, purchasedSetSoFar
        )

        new_bposCount = bposBoughtSoFar + bBought
        total_jumps = baseJumps + stVisitedCount

        # skip if over jump limit
        if total_jumps > maxJumps:
            continue

        # Multi-criteria check
        fsPurch = frozenset(newPurchSet)
        old_record = visited.get((neighborSys, newBgt, fsPurch), ( -1, 9999999 ))
        old_bpos, old_jumps = old_record

        # We only prune if new state is strictly worse:
        # "strictly worse" means new_bposCount <= old_bpos AND total_jumps >= old_jumps
        if not (new_bposCount <= old_bpos and total_jumps >= old_jumps):
            visited[(neighborSys, newBgt, fsPurch)] = (new_bposCount, total_jumps)

            new_path = pathSoFar + [(neighborSys, stPurch)]
            new_state = (
                neighborSys,
                newBgt,
                total_jumps,
                new_bposCount,
                new_path,
                newPurchSet
            )
            queue.append(new_state)

# -----------------------------
# 6) Print results
# -----------------------------
if best_path is None:
    print(f"No route found from {LOCATION} to {DESTINATION} within {maxJumps} jumps.")
else:
    print("=== Best Route Found ===")
    print(f"Start: {LOCATION}, Destination: {DESTINATION}")
    print(f"Jumps: {best_jumps}")
    print(f"BPOs Purchased: {best_bpos}")
    if best_jumps > 0:
        print(f"BPOs per Jump: {best_bpos / best_jumps:.2f}")
    else:
        print("BPOs per Jump: N/A")
    print()
    
    if best_bpos >= 100:
        stop_counter = 1
        for sys_id, station_list in best_path:
            # Only print if we actually bought something
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
        purchasesBPs = set()
        stop_counter = 1
        for sys_id, station_list in best_path:
            # Only print if we actually bought something
            station_purchases = []
            for (stName, bpsBought) in station_list:
                if bpsBought:
                    station_purchases.append((stName, bpsBought))

            if station_purchases:
                print(f"Stop {stop_counter}: System {sys_id}")
                for (stName, bpsBought) in station_purchases:
                    print(f"  - Station: {stName}")
                    for bp in bpsBought:
                        purchasesBPs.add(bp)
                    print()
                stop_counter += 1
        print("\nShopping List:")
        for bp in purchasesBPs:
            print(bp)
