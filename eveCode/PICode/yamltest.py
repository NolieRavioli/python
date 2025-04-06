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

# Region and Station mappings
REGIONS = {
    "Domain": 10000043,
    "The Forge": 10000002,
    "Sinq Laison": 10000032,
    "Heimatar": 10000030,
    "Metropolis": 10000042
}

STATIONS = {
    "Jita": 60003760,
    "Amarr": 60008494,
    "Dodixie": 60011866,
    "Rens": 60004588,
    "Hek": 60005686
}

STATION_TO_REGION = {
    "Jita": "The Forge",
    "Amarr": "Domain",
    "Dodixie": "Sinq Laison",
    "Rens": "Heimatar",
    "Hek": "Metropolis"
}

def parse_schematics(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)

    schematics = []
    
    for schematic_id, schematic_info in data.items():
        name_en = schematic_info['nameID']['en']
        cycleTime = schematic_info['cycleTime']
        inputs = {}
        output = None

        for type_id, type_info in schematic_info['types'].items():
            if type_info['isInput']:
                inputs[type_id] = type_info['quantity']
            else:
                output = (type_id, type_info['quantity'])

        schematics.append({
            'name': name_en,
            'cycleTime': cycleTime,
            'inputs': inputs,
            'output': output
        })

    return schematics

def build_all_pi_chains(schematics):
    chains = []

    for schematic in schematics:
        level = classify_tier(schematic, schematics)
        chain = build_pi_chain(schematic, schematics, level=level)
        chains.append(chain)

    return chains

def classify_tier(schematic, schematics):
    inputs = schematic['inputs']
    max_input_tier = 0

    for input_id in inputs:
        input_schematic = next((s for s in schematics if s['output'][0] == input_id), None)
        if input_schematic:
            input_tier = classify_tier(input_schematic, schematics)
            max_input_tier = max(max_input_tier, input_tier)

    return max_input_tier + 1

def build_pi_chain(schematic, schematics, chain=None, total_quantity=None, level=4):
    if chain is None:
        chain = {}
    if total_quantity is None:
        total_quantity = schematic['output'][1]

    output_id, output_quantity = schematic['output']
    chain[schematic['name']] = {
        'level': level,
        'output': output_id,
        'quantity': total_quantity
    }

    for input_id, input_quantity in schematic['inputs'].items():
        required_quantity = total_quantity * input_quantity / output_quantity
        next_schematic = next((s for s in schematics if s['output'][0] == input_id), None)

        if next_schematic:
            next_level = classify_tier(next_schematic, schematics)
            build_pi_chain(next_schematic, schematics, chain, required_quantity, next_level)
        else:
            chain[f"Raw Material {input_id}"] = {
                'level': 0,
                'output': input_id,
                'quantity': required_quantity
            }

    return chain

def get_volume_adjusted_input_cost(type_id, total_quantity_needed, price_type, station_name):
    with open(MARKET_FILE, 'r') as file:
        market_orders = json.load(file)

    orders = market_orders.get(str(type_id), [])
    if not orders:
        return None

    location_id = STATIONS.get(station_name)

    filtered_orders = [
        order for order in orders
        if (order['location_id'] == location_id) and (order['is_buy_order'] == (price_type == 'maxBuy'))
    ]

    if not filtered_orders:
        return None

    filtered_orders.sort(key=lambda x: x['price'], reverse=(price_type == 'maxBuy'))

    total_cost = 0
    volume_accumulated = 0

    for order in filtered_orders:
        available_volume = order['volume_remain']
        price = order['price']

        if volume_accumulated + available_volume >= total_quantity_needed:
            total_cost += (total_quantity_needed - volume_accumulated) * price * (100 + piTax) / 100
            return total_cost
        else:
            total_cost += available_volume * price * (100 + piTax) / 100
            volume_accumulated += available_volume

    return total_cost

def calculate_profitability(pi_chain_dicts, price_type, station_name):
    allChainProf = {}
    for pi_chain_dict in pi_chain_dicts:
        pi_chain_items = list(pi_chain_dict.keys())
        output = pi_chain_items[0]
        outId = pi_chain_dict[output]['output']
        endLevel = pi_chain_dict[output]['level']
        for startLevel in range(0, endLevel):
            l2lCost = 0
            outputPrice = get_volume_adjusted_input_cost(outId, 1, price_type, station_name) * pi_chain_dict[output]['quantity']
            for item in pi_chain_items[1:]:
                if pi_chain_dict[item]['level'] == startLevel:
                    l2lCost += get_volume_adjusted_input_cost(
                        pi_chain_dict[item]['output'],
                        pi_chain_dict[item]['quantity'], price_type, station_name)
            profit = outputPrice - l2lCost
            allChainProf[f'T{startLevel} to {output}'] = profit

    sorted_allChainProf = dict(sorted(allChainProf.items(), key=lambda item: item[1], reverse=True))
    return sorted_allChainProf

def get_type_ids(item_names):
    return {item_id: item_id for item_id in item_names}

def update_market_orders(region_name, type_ids):
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

    def calculate():
        selected_price_type = price_type_dropdown.get()
        selected_station = station_dropdown.get()

        # Parse schematics and build PI chains
        schematics = parse_schematics(FILE_PATH)
        pi_chains = build_all_pi_chains(schematics)

        # Process and sort the chains
        pi_chain_dicts = []
        for chain in pi_chains:
            sorted_chain = sorted(chain.items(), key=lambda x: x[1]['level'], reverse=True)
            pi_chain_dict = {name: info for name, info in sorted_chain}
            pi_chain_dicts.append(pi_chain_dict)
        pi_chain_dicts = sorted(pi_chain_dicts, key=lambda x: len(x), reverse=True)

        # Calculate profitability
        sorted_allChainProf = calculate_profitability(pi_chain_dicts, selected_price_type, selected_station)
        results_text.delete("1.0", tk.END)
        results_text.insert(tk.END, json.dumps(sorted_allChainProf, indent=4))

    def update_prices():
        selected_station = station_dropdown.get()
        region_name = STATION_TO_REGION.get(selected_station)

        schematics = parse_schematics(FILE_PATH)
        item_names = [item for schematic in schematics for item in list(schematic["inputs"].keys()) + [schematic["output"][0]]]
        type_ids = get_type_ids(item_names)

        if region_name and type_ids:
            update_market_orders(region_name, type_ids)
            print(f"Updated market orders for {region_name}.")

    update_button = tk.Button(root, text="Update Prices", command=update_prices)
    update_button.pack()

    calculate_button = tk.Button(root, text="Calculate Profitability", command=calculate)
    calculate_button.pack()

    results_text = tk.Text(root, wrap='word', height=20, width=80)
    results_text.pack()

    root.mainloop()

if __name__ == "__main__":
    create_gui()
