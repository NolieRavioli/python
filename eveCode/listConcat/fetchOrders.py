import requests
import json
import csv
##import time  # To prevent excessive API calls

# Define the API endpoint
BASE_URL = "https://evetycoon.com/api/v1/market/orders/"

# Load base prices from CSV
base_prices = {}

csv_file = "list1_with_prices.txt"  # Ensure this file is in the same directory

try:
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)  # Reads CSV with headers: name, bpId, basePrice
        for row in reader:
            try:
                bp_id = int(row["bpId"])
                base_price = float(row["basePrice"])
                base_prices[bp_id] = base_price
            except ValueError:
                print(f"Skipping invalid row in CSV: {row}")  # Debugging if bad data
except FileNotFoundError:
    print(f"Error: CSV file '{csv_file}' not found!")
    exit(1)

# Initialize the final marketOrders dictionary
marketOrders = {}

total = len(base_prices.keys())
count = 0

# Loop over all typeIds in base_prices
for type_id in base_prices.keys():
    print(f"processing ({count}/{total}) {100*count/total:.2f}%")
    url = f"{BASE_URL}{type_id}"
##    print(f"Fetching market data for Type ID {type_id} from: {url}")  # Debug: Print API request URL

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        # Debug: Print how many orders were retrieved
##        print(f"Total Orders Retrieved for {type_id}: {len(data.get('orders', []))}")

        # Get station and structure names
        station_names = data.get("stationNames", {})
        structure_names = data.get("structureNames", {})

        for order in data.get("orders", []):
            if order["isBuyOrder"]:
                continue  # Skip buy orders

            price = order["price"]

            # Get base price from CSV
            base_price = base_prices.get(type_id, None)

            # If base price exists, apply 1.05x filtering
            if base_price and price > 1.05 * base_price:
                continue  # Skip overpriced orders

            location_id = order["locationId"]

            # Get the station or structure name
            station_name = station_names.get(str(location_id), structure_names.get(str(location_id), ""))

            # Get system name
            system_id = str(order["systemId"])
            system_name = data["systems"].get(system_id, {}).get("solarSystemName", "")

            # If there's already an entry, keep the lowest price
            if location_id not in marketOrders:
                marketOrders[location_id] = {
                        "stationName": station_name,
                        "systemName": system_name,
                        "systemId": order["systemId"]
                    }

            if type_id not in marketOrders[location_id] or price < marketOrders[location_id][type_id]["price"]:
                item_name = data['itemType']['typeName']
                marketOrders[location_id][type_id] = {
                    "itemName": item_name,
                    "locationId": location_id,
                    "minVolume": order["minVolume"],
                    "orderId": order["orderId"],
                    "price": price,
                    "systemId": order["systemId"],
                    "regionId": order["regionId"],
                    "typeId": type_id,
                    "volumeRemain": order["volumeRemain"],
                    "volumeTotal": order["volumeTotal"],
                    "stationName": station_name,
                    "systemName": system_name
                }
    else:
        print(f"Error fetching data for Type ID {type_id}: {response.status_code}, {response.text}")  # Debug: Print API error response

    # Sleep to avoid hitting rate limits (adjust delay as needed)
##    time.sleep(0.5)  # 500ms delay between requests
    count += 1

# Save to a JSON file
with open("marketOrders.json", "w") as f:
    json.dump(marketOrders, f, indent=4)

print("Market orders saved to marketOrders.json")
