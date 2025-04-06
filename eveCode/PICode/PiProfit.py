import requests
import re
import json
import tkinter as tk
from tkinter import ttk
import time

taxPercent = 4.46
piTax = 15.8

# File containing PI schematics
FILE_PATH = "pi_chains.json"
MARKET_FILE = "marketOrders.json"

# ESI endpoint for market orders with type ID and region ID
ESI_MARKET_ENDPOINT = "https://esi.evetech.net/latest/markets/{region_id}/orders/"

# Region IDs
REGIONS = {
    "Domain": 10000043,    # Domain region ID (Amarr)
    "The Forge": 10000002, # The Forge region ID (Jita)
    "Sinq Laison": 10000032, # Sinq Laison region ID (Dodixie)
    "Heimatar": 10000030,  # Heimatar region ID (Rens)
    "Metropolis": 10000042, # Metropolis region ID (Hek)
    "Parrigen Falls":10000066
}

# Station IDs
STATIONS = {
    "Jita": 60003760,
    "Amarr": 60008494,
    "Dodixie": 60011866,
    "Rens": 60004588,
    "Hek": 60005686,
    "Beanstar":1038457641673
}

# Mapping station to region
STATION_TO_REGION = {
    "Jita": "The Forge",
    "Amarr": "Domain",
    "Dodixie": "Sinq Laison",
    "Rens": "Heimatar",
    "Hek": "Metropolis",
    "Beanstar":"Parrigen Falls"
}

# Function to parse the input file with new format
def parse_schematics(file_path):
    schematics = []
    current_schematic = None

    with open(file_path, 'r') as file:
        lines = file.readlines()

        for line in lines:
            line = line.rstrip()

            # Detect schematic output
            if line.startswith("Schematic "):
                if current_schematic:
                    schematics.append(current_schematic)
                current_schematic = {"output": line.replace("Schematic ", ""), "inputs": {}}

            # Detect input items with exactly 6 leading spaces
            elif line.startswith("      ") and line[6] != ' ':
                match = re.match(r"(.+?)\s+(\d+)", line.strip())
                if match:
                    item, quantity = match.groups()
                    current_schematic["inputs"][item] = int(quantity)

        if current_schematic:
            schematics.append(current_schematic)

    return schematics

# Function to get type IDs for items, ensuring uniqueness and sending as a JSON array
def get_type_ids(item_names, batch_size=100):
    type_ids = {}
    unique_names = list(set(item_names))  # Ensure unique item names

    for i in range(0, len(unique_names), batch_size):
        batch = unique_names[i:i + batch_size]
        try:
            response = requests.post(
                "https://esi.evetech.net/latest/universe/ids/",
                headers={"Content-Type": "application/json"},
                data=json.dumps(batch)
            )

            if response.status_code == 200:
                data = response.json()
                type_ids.update({entry['name']: entry['id'] for entry in data.get('inventory_types', [])})
            else:
                print(f"Failed to get type IDs: {response.status_code} - {response.text}")
                return {}
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return {}

    return type_ids

# Function to update market orders and save to a file using the ESI endpoint
def update_market_orders(region_name):
    region_id = REGIONS.get(region_name)
    if not region_id:
        print("Invalid region selected.")
        return

    all_items = list(type_ids.values())
    market_orders = {}

    total_items = len(all_items)
    for idx, type_id in enumerate(all_items):
        page = 1
        total_orders = []
        retries = 0

        while True:
            try:
                response = requests.get(
                    ESI_MARKET_ENDPOINT.format(region_id=region_id),
                    params={'type_id': type_id, 'order_type': 'sell', 'page': page}
                )

                if response.status_code == 200:
                    orders = response.json()
                    total_orders.extend(orders)

                    # Check if there are more pages to process
                    total_pages = int(response.headers.get('X-Pages', 1))
                    if page >= total_pages:
                        break

                    page += 1

                elif response.status_code == 504:
                    # Retry after 200ms if 504 error occurs
                    if retries < 3:
                        retries += 1
                        print(f"504 error for Type ID {type_id}, retrying ({retries}/3)...")
                        time.sleep(0.2)
                    else:
                        print(f"Failed to retrieve data for Type ID {type_id} after 3 retries.")
                        break

                else:
                    print(f"Failed to get market data for Type ID {type_id}: {response.status_code}")
                    break

            except requests.exceptions.RequestException as e:
                print(f"Request failed for Type ID {type_id}: {e}")
                break

        # Save all orders for the type ID
        market_orders[type_id] = total_orders

        # Print progress percentage
        progress = (idx + 1) / total_items * 100
        print(f"Progress: {progress:.2f}%")

    with open(MARKET_FILE, 'w') as file:
        json.dump(market_orders, file)

# Function to get the input cost considering volume of orders
def get_volume_adjusted_input_cost(type_id, total_quantity_needed, price_type, station_name):
    with open(MARKET_FILE, 'r') as file:
        market_orders = json.load(file)

    orders = market_orders.get(str(type_id), [])
    if not orders:
        return None

    location_id = STATIONS.get(station_name)

    # Filter by location and price type
    filtered_orders = [
        order for order in orders
        if order['location_id'] == location_id and order['is_buy_order'] == (price_type == 'maxBuy')
    ]

    # Sort orders by price: ascending for minSell, descending for maxBuy
    filtered_orders.sort(key=lambda x: x['price'], reverse=(price_type == 'maxBuy'))

    total_cost = 0
    volume_accumulated = 0

    # Accumulate cost based on available volume
    for order in filtered_orders:
        available_volume = order['volume_remain']
        price = order['price']

        if volume_accumulated + available_volume >= total_quantity_needed:
            total_cost += (total_quantity_needed - volume_accumulated) * price * (100 + piTax) / 100
            volume_accumulated = total_quantity_needed
            break
        else:
            total_cost += available_volume * price * (100 + piTax) / 100
            volume_accumulated += available_volume

    if volume_accumulated < total_quantity_needed:
        print(f"Insufficient volume for Type ID {type_id} at {station_name}. Needed: {total_quantity_needed}, available: {volume_accumulated}")
        return None

    return total_cost

# Function to get the output price
def get_output_price(type_id, price_type, station_name):
    with open(MARKET_FILE, 'r') as file:
        market_orders = json.load(file)

    orders = market_orders.get(str(type_id), [])
    if not orders:
        return None

    location_id = STATIONS.get(station_name)

    # Filter orders by location and price type
    filtered_orders = [
        order for order in orders
        if order['location_id'] == location_id and order['is_buy_order'] == (price_type == 'maxBuy')
    ]

    # Return the best price based on price type
    if filtered_orders:
        if price_type == 'maxBuy':
            return max(order['price'] for order in filtered_orders) * (100 - taxPercent) / 100
        else:  # 'minSell'
            return min(order['price'] for order in filtered_orders) * (100 - taxPercent) / 100

    return None

# Function to calculate profitability for each schematic
def calculate_profitability(price_type, station_name):
    if station_name not in STATIONS:
        print("Invalid station selected.")
        return

    # Calculate profitability for each schematic
    for schematic in schematics:
        output_item = schematic['output']
        output_type_id = type_ids.get(output_item)
        output_price = get_output_price(output_type_id, price_type, station_name) if output_type_id else None

        # Calculate total input cost by multiplying inputs by 37
        total_input_cost = 0
        for item, quantity in schematic['inputs'].items():
            total_quantity_needed = quantity * 1  # Multiply by 37
            type_id = type_ids.get(item)
            if type_id:
                cost = get_volume_adjusted_input_cost(type_id, total_quantity_needed, price_type, station_name)
                if cost:
                    total_input_cost += cost
                else:
                    print(f"Could not find sufficient volume for {item}.")
            else:
                print(f"Could not retrieve Type ID for {item}.")

        # Calculate average input cost per output
        average_input_cost = total_input_cost if total_input_cost > 0 else None

        # Calculate and display profitability
        if output_price and average_input_cost is not None:
            profit = output_price - average_input_cost
            print(f"Schematic: {output_item}")
            print(f"  Output Price: {output_price} ISK")
            print(f"  Average Input Cost: {average_input_cost} ISK")
            print(f"  Profitability: {profit} ISK\n")
        else:
            print(f"Could not find sufficient volume for {output_item}.")

# GUI for the program
def create_gui():
    root = tk.Tk()
    root.title("EVE PI Profitability Calculator")

    # Dropdown for selecting price type
    price_type_label = tk.Label(root, text="Price Type:")
    price_type_label.pack()
    price_type_dropdown = ttk.Combobox(root, values=["maxBuy", "minSell"])
    price_type_dropdown.set("minSell")
    price_type_dropdown.pack()

    # Dropdown for selecting station
    station_label = tk.Label(root, text="Station:")
    station_label.pack()
    station_dropdown = ttk.Combobox(root, values=list(STATIONS.keys()))
    station_dropdown.set("Amarr")
    station_dropdown.pack()

    # Button for updating prices
    def update_prices():
        selected_station = station_dropdown.get()
        region_name = STATION_TO_REGION.get(selected_station)

        if region_name:
            update_market_orders(region_name)
            print(f"Updated market orders for {region_name}.")
        else:
            print("Invalid station selected.")

    update_button = tk.Button(root, text="Update Prices", command=update_prices)
    update_button.pack()

    # Button for calculating profitability
    def calculate():
        selected_price_type = price_type_dropdown.get()
        selected_station = station_dropdown.get()
        calculate_profitability(selected_price_type, selected_station)

    calculate_button = tk.Button(root, text="Calculate Profitability", command=calculate)
    calculate_button.pack()

    root.mainloop()

if __name__ == "__main__":
    schematics = parse_schematics(FILE_PATH)
    type_ids = get_type_ids([item for schematic in schematics for item in list(schematic["inputs"].keys()) + [schematic["output"]]])

    create_gui()
