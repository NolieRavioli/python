import requests
import json
import yaml
import tkinter as tk
from tkinter import ttk
import time

taxPercent = 4.46
piTax = 15.8

# File containing PI schematics in YAML format
FILE_PATH = "planetSchematics.yaml"
MARKET_FILE = "marketOrders.json"

# ESI endpoint for market orders with type ID and region ID
ESI_MARKET_ENDPOINT = "https://esi.evetech.net/latest/markets/{region_id}/orders/"

# Region IDs
REGIONS = {
    "Domain": 10000043,
    "The Forge": 10000002,
    "Sinq Laison": 10000032,
    "Heimatar": 10000030,
    "Metropolis": 10000042
}

# Station IDs
STATIONS = {
    "Jita": 60003760,
    "Amarr": 60008494,
    "Dodixie": 60011866,
    "Rens": 60004588,
    "Hek": 60005686
}

# Mapping station to region
STATION_TO_REGION = {
    "Jita": "The Forge",
    "Amarr": "Domain",
    "Dodixie": "Sinq Laison",
    "Rens": "Heimatar",
    "Hek": "Metropolis"
}

# Function to parse the YAML file for schematics
def parse_schematics(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)

    schematics = []
    
    # Iterate through each schematic
    for schematic_id, schematic_info in data.items():
        name_en = schematic_info['nameID']['en']
        inputs = {}
        output = None

        # Go through types to identify inputs and outputs
        for type_id, type_info in schematic_info['types'].items():
            if type_info['isInput']:
                inputs[type_id] = type_info['quantity']
            else:
                output = (type_id, type_info['quantity'])

        schematics.append({
            'name': name_en,
            'inputs': inputs,
            'output': output
        })

    return schematics

# Helper function to determine the level of each product
def determine_levels(schematics):
    # Create a mapping of outputs to their respective schematics
    output_map = {s['output'][0]: s for s in schematics}
    levels = {}

    # Recursive function to calculate the level of a product
    def get_level(type_id):
        if type_id not in output_map:
            return 0  # Raw material

        if type_id in levels:
            return levels[type_id]  # Already calculated

        schematic = output_map[type_id]
        max_input_level = max(get_level(input_id) for input_id in schematic['inputs'])

        levels[type_id] = max_input_level + 1
        return levels[type_id]

    # Calculate levels for all schematics
    for schematic in schematics:
        output_type_id = schematic['output'][0]
        get_level(output_type_id)

    return levels

# Function to get type IDs for items (already provided as type IDs in this case)
def get_type_ids(item_ids):
    return {item_id: item_id for item_id in item_ids}

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

                    total_pages = int(response.headers.get('X-Pages', 1))
                    if page >= total_pages:
                        break

                    page += 1

                elif response.status_code == 504:
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

        market_orders[type_id] = total_orders
        progress = (idx + 1) / total_items * 100
        print(f"Progress: {progress:.2f}%")

    with open(MARKET_FILE, 'w') as file:
        json.dump(market_orders, file)

# Function to get the output price
def get_output_price(type_id, price_type, station_name):
    with open(MARKET_FILE, 'r') as file:
        market_orders = json.load(file)

    orders = market_orders.get(str(type_id), [])
    if not orders:
        return None

    location_id = STATIONS.get(station_name)

    filtered_orders = [
        order for order in orders
        if order['location_id'] == location_id and order['is_buy_order'] == (price_type == 'maxBuy')
    ]

    if filtered_orders:
        if price_type == 'maxBuy':
            return max(order['price'] for order in filtered_orders) * (100 - taxPercent) / 100
        else:
            return min(order['price'] for order in filtered_orders) * (100 - taxPercent) / 100

    return None

# Function to get the input cost considering volume of orders
def get_volume_adjusted_input_cost(type_id, total_quantity_needed, price_type, station_name):
    with open(MARKET_FILE, 'r') as file:
        market_orders = json.load(file)

    orders = market_orders.get(str(type_id), [])
    if not orders:
        return None

    location_id = STATIONS.get(station_name)

    filtered_orders = [
        order for order in orders
        if order['location_id'] == location_id and order['is_buy_order'] == (price_type == 'maxBuy')
    ]

    filtered_orders.sort(key=lambda x: x['price'], reverse=(price_type == 'maxBuy'))

    total_cost = 0
    volume_accumulated = 0

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

# Recursive function to calculate profitability across different levels of PI chains
def calculate_chain_profitability(schematic_name, quantity, price_type, station_name, level=1):
    schematic = next((s for s in schematics if s['name'] == schematic_name), None)
    if not schematic:
        print(f"Schematic {schematic_name} not found.")
        return None

    output_type_id, output_quantity = schematic['output']
    output_price = get_output_price(output_type_id, price_type, station_name)

    total_input_cost = 0

    for input_id, input_quantity in schematic['inputs'].items():
        total_quantity_needed = input_quantity * quantity

        # Check if the input is a raw material or a product of another schematic
        input_schematic = next((s for s in schematics if s['output'][0] == input_id), None)
        if input_schematic:
            # Calculate the cost recursively for intermediate products
            sub_cost = calculate_chain_profitability(input_schematic['name'], input_quantity, price_type, station_name, level + 1)
            if sub_cost is not None:
                total_input_cost += sub_cost
        else:
            # Calculate the cost for raw materials from the market
            cost = get_volume_adjusted_input_cost(input_id, total_quantity_needed, price_type, station_name)
            if cost is not None:
                total_input_cost += cost

    if output_price is not None and total_input_cost > 0:
        profit = (output_price * quantity) - total_input_cost
        print(f"Level {level} - {schematic_name}")
        print(f"  Total Input Cost: {total_input_cost / quantity} ISK per unit")
        print(f"  Output Price: {output_price} ISK per unit")
        print(f"  Profitability: {profit / quantity} ISK per unit\n")

    return total_input_cost

# GUI for the program
def create_gui():
    root = tk.Tk()
    root.title("EVE PI Profitability Calculator")

    price_type_label = tk.Label(root, text="Price Type:")
    price_type_label.pack()
    price_type_dropdown = ttk.Combobox(root, values=["maxBuy", "minSell"])
    price_type_dropdown.set("minSell")
    price_type_dropdown.pack()

    station_label = tk.Label(root, text="Station:")
    station_label.pack()
    station_dropdown = ttk.Combobox(root, values=list(STATIONS.keys()))
    station_dropdown.set("Amarr")
    station_dropdown.pack()

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

    def calculate():
        selected_price_type = price_type_dropdown.get()
        selected_station = station_dropdown.get()
        for schematic in schematics:
            calculate_chain_profitability(schematic['name'], 1, selected_price_type, selected_station)

    calculate_button = tk.Button(root, text="Calculate Profitability", command=calculate)
    calculate_button.pack()

    root.mainloop()

if __name__ == "__main__":
    schematics = parse_schematics(FILE_PATH)
    levels = determine_levels(schematics)
    type_ids = get_type_ids([item for schematic in schematics for item in list(schematic["inputs"].keys()) + [schematic["output"][0]]])

    create_gui()
