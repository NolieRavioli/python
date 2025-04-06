import json

BUDGET = 100_000_000  # 100 million ISK

# Load market data
with open('marketOrders.json', 'r') as f:
    data = json.load(f)

# Load owned blueprints and filter them out
with open('list2.txt', 'r') as f:
    tmp = f.readlines()
    owned_bps = set(i.split('\t')[0].strip() for i in tmp)

# Load precomputed jump distances from MJ-5F9
with open('precomputed_routes.json', 'r') as f:
    jump_distances = json.load(f)

# Dictionary to store station blueprint counts and distances
station_data = {}

for locID, items in data.items():
    if "stationName" not in items or "systemId" not in items:
        continue  # Skip malformed entries

    system_id = str(items['systemId'])  # Convert to string to match JSON keys
    jump_distance = jump_distances.get(system_id, float('inf'))  # Default to a high value if missing

    blueprint_list = []

    for itemID, order in items.items():
        if not itemID.isdigit():  # Skip metadata keys
            continue

        currItemName = order['itemName']
        price = order['price']

        if currItemName in owned_bps:
            continue  # Ignore owned blueprints

        blueprint_list.append((currItemName, price))

    # Sort blueprints by price (cheapest first)
    blueprint_list.sort(key=lambda x: x[1])

    # Purchase as many BPs as possible within 100 million ISK
    total_cost = 0
    purchased_bps = set()

    for bp_name, bp_price in blueprint_list:
        if total_cost + bp_price > BUDGET:
            break
        total_cost += bp_price
        purchased_bps.add(bp_name)

    # Store station results
    station_data[locID] = {
        "bp_count": len(purchased_bps),
        "station_name": items['stationName'],
        "jump_distance": jump_distance,
        'bps': purchased_bps
    }

# Sort first by jump distance (ascending), then by blueprint count (descending)
sorted_stations = sorted(station_data.items(), key=lambda x: (-x[1]["bp_count"], x[1]["jump_distance"]))
# Print top 3 stations
for locID, info in sorted_stations[:6]:
    print(f"{info['station_name']} - {info['bp_count']} blueprints within 100M ISK, {info['jump_distance']} jumps away")
    for bp in info['bps']:
        print(bp)
