import json
import requests
import yaml
import time
from collections import defaultdict

# File paths
PRECOMPUTED_ROUTES_PATH = "precomputed_routes.json"
BPO_LIST_PATH = "tabSeperatedBPOList.txt"
TYPES_YAML_PATH = r"C:\\Users\\nolan\\Downloads\\fsd\\types.yaml"
OUTPUT_FILE = "locationItems.json"
MARKET_API_URL = "https://evetycoon.com/api/v1/market/orders/{}"
ISK_LIMIT = 100_000_000

# Load precomputed routes
with open(PRECOMPUTED_ROUTES_PATH, "r") as f:
    precomputed_routes = json.load(f)

# Load tab-separated BPO list
blueprint_ids = set()
with open(BPO_LIST_PATH, "r", encoding="utf-8") as f:
    next(f)  # Skip header
    for line in f:
        parts = line.strip().split("\t")
        blueprint_id = parts[2]
        blueprint_ids.add(blueprint_id)

# Load types.yaml with fast parsing
with open(TYPES_YAML_PATH, "r", encoding="utf-8") as f:
    types_data = yaml.load(f, Loader=yaml.CLoader)

# Cache for API responses
market_cache = {}

def get_market_orders(type_id):
    """Fetch market orders for a given type_id with caching and error handling."""
    if type_id in market_cache:
        return market_cache[type_id]
    try:
        response = requests.get(MARKET_API_URL.format(type_id), timeout=10)
        response.raise_for_status()
        data = response.json()
        market_cache[type_id] = data
        time.sleep(0.5)  # Prevent rate-limiting
        return data
    except requests.RequestException as e:
        print(f"Error fetching {type_id}: {e}")
        return None

print('Loaded YAMLs')
print(f"Total blueprints loaded: {len(blueprint_ids)}")

# Dictionary to store market orders
market_orders = defaultdict(lambda: defaultdict(float))
metadata = {"systems": {}, "stationNames": {}, "structureNames": {}, "typeNames": {}}

total = len(blueprint_ids)
count = 0
start_time = time.time()

for type_id in blueprint_ids:
    data = get_market_orders(type_id)
    if not data:
        continue

    metadata["typeNames"][type_id] = data["itemType"]["typeName"]
    metadata["systems"].update(data["systems"])
    metadata["stationNames"].update(data.get("stationNames", {}))
    metadata["structureNames"].update(data.get("structureNames", {}))

    if not data["orders"]:
        print(f"No market orders found for {type_id}")
        continue

    base_price = types_data.get(int(type_id), {}).get("basePrice", None)
    if base_price is None:
        continue

    for order in data["orders"]:
        if not order["isBuyOrder"]:  # Only consider sell orders
            location_id = order["locationId"]
            price = order["price"]
            
            if price <= base_price * 1.05:  # Only keep orders within 105% of base price
                if type_id not in market_orders[location_id] or market_orders[location_id][type_id] > price:
                    market_orders[location_id][type_id] = price
    count += 1
    elapsed_time = time.time() - start_time
    eta = (elapsed_time / count) * (total - count) if count else 0
    print(f'Processing {count}/{total} ({100*count/total:.2f}%) - ETA: {eta:.2f}s')

print(f"Total locations with market orders: {len(market_orders)}")

# Process affordable blueprints per location
affordable_locations = {}
for location, items in market_orders.items():
    sorted_items = sorted(items.items(), key=lambda x: x[1])  # Sort by price
    total_price = 0
    selected_items = {}

    for type_id, price in sorted_items:
        if total_price + price > ISK_LIMIT:
            break
        selected_items[type_id] = price
        total_price += price

    if selected_items:
        affordable_locations[location] = selected_items

print(f"Total locations with affordable blueprints: {len(affordable_locations)}")

# Save to file
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump({"locations": affordable_locations, "metadata": metadata}, f, indent=4)

# Find top 10 locations with the most affordable BPs
top_locations = sorted(affordable_locations.items(), key=lambda x: len(x[1]), reverse=True)[:10]

print("Top 10 locations with the most affordable blueprints:")
if not top_locations:
    print("No locations found with affordable blueprints.")
else:
    for location, items in top_locations:
        system_id = next((sid for sid, details in metadata["systems"].items() if sid in precomputed_routes), "Unknown")
        system_name = metadata["systems"].get(system_id, {}).get("solarSystemName", "Unknown")
        station_name = metadata["stationNames"].get(location, metadata["structureNames"].get(location, "Unknown"))
        jump_distance = precomputed_routes.get(system_id, "Unknown")
        print(f"Location ID: {location} | System: {system_name} | Station: {station_name} | BPs: {len(items)} | Jumps: {jump_distance}")
