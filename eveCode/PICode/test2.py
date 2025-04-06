import requests
import json
import webbrowser
import tkinter as tk
from tkinter import ttk
import http.server
import socketserver
import re

# ======================
# OAuth2 / ESI Constants
# ======================
CLIENT_ID = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
SECRET_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
REDIRECT_URI = "http://localhost:8080/callback"
SCOPES = ' '.join([
    "publicData", "esi-calendar.read_calendar_events.v1", "esi-location.read_location.v1",
    "esi-location.read_ship_type.v1", "esi-mail.organize_mail.v1", "esi-mail.read_mail.v1",
    "esi-mail.send_mail.v1", "esi-skills.read_skills.v1", "esi-skills.read_skillqueue.v1",
    "esi-wallet.read_character_wallet.v1", "esi-wallet.read_corporation_wallet.v1",
    "esi-search.search_structures.v1", "esi-clones.read_clones.v1", "esi-characters.read_contacts.v1",
    "esi-universe.read_structures.v1", "esi-bookmarks.read_character_bookmarks.v1",
    "esi-killmails.read_killmails.v1", "esi-corporations.read_corporation_membership.v1",
    "esi-assets.read_assets.v1", "esi-planets.manage_planets.v1", "esi-fleets.read_fleet.v1",
    "esi-ui.open_window.v1", "esi-ui.write_waypoint.v1", "esi-fittings.read_fittings.v1",
    "esi-markets.structure_markets.v1", "esi-corporations.read_structures.v1",
    "esi-characters.read_loyalty.v1", "esi-characters.read_standings.v1",
    "esi-characters.read_agents_research.v1", "esi-industry.read_character_jobs.v1",
    "esi-markets.read_character_orders.v1", "esi-characters.read_blueprints.v1",
    "esi-characters.read_corporation_roles.v1", "esi-location.read_online.v1",
    "esi-contracts.read_character_contracts.v1", "esi-clones.read_implants.v1",
    "esi-characters.read_fatigue.v1", "esi-killmails.read_corporation_killmails.v1",
    "esi-corporations.track_members.v1", "esi-wallet.read_corporation_wallets.v1",
    "esi-characters.read_notifications.v1", "esi-corporations.read_divisions.v1",
    "esi-corporations.read_contacts.v1", "esi-assets.read_corporation_assets.v1",
    "esi-corporations.read_blueprints.v1", "esi-bookmarks.read_corporation_bookmarks.v1",
    "esi-contracts.read_corporation_contracts.v1", "esi-corporations.read_standings.v1",
    "esi-corporations.read_starbases.v1", "esi-industry.read_corporation_jobs.v1",
    "esi-markets.read_corporation_orders.v1", "esi-corporations.read_container_logs.v1",
    "esi-industry.read_character_mining.v1", "esi-industry.read_corporation_mining.v1",
    "esi-planets.read_customs_offices.v1", "esi-corporations.read_facilities.v1",
    "esi-alliances.read_contacts.v1", "esi-characters.read_fw_stats.v1",
    "esi-corporations.read_fw_stats.v1", "esi-characterstats.read.v1"
])
AUTH_URL = f"https://login.eveonline.com/v2/oauth/authorize/?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope={SCOPES}&state=auth_request"
TOKEN_URL = "https://login.eveonline.com/v2/oauth/token"

# Beanstar structure ID
BEANSTAR_STRUCTURE_ID = 1038457641673

# File paths
PI_CHAINS_FILE = "pi_chains.json"
UNIQUE_ITEMS_FILE = "unique_items.json"
MARKET_FILE = "marketOrders.json"

# Global variable for access token
access_token = None

# Station IDs
STATIONS = {
    "Beanstar": BEANSTAR_STRUCTURE_ID
}

# ======================
# OAuth2 Authentication
# ======================
class OAuthCallbackHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global access_token
        if "/callback" in self.path:
            code = self.path.split("code=")[1].split("&")[0]
            response = requests.post(
                TOKEN_URL,
                auth=(CLIENT_ID, SECRET_KEY),
                data={"grant_type": "authorization_code", "code": code},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            if response.status_code == 200:
                tokens = response.json()
                access_token = tokens["access_token"]
                print("Access token received!")
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"<html><body><h1>Authentication Successful!</h1></body></html>")
            else:
                print("Failed to get access token:", response.text)

def get_auth_token():
    global access_token
    print("Opening browser for authentication...")
    webbrowser.open(AUTH_URL)
    with socketserver.TCPServer(("localhost", 8080), OAuthCallbackHandler) as httpd:
        httpd.handle_request()

# ======================
# Market Data functions
# ======================
def fetch_market_orders():
    if not access_token:
        print("You need to authenticate first.")
        return

    base_url = f"https://esi.evetech.net/latest/markets/structures/{BEANSTAR_STRUCTURE_ID}/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    all_orders = []
    page = 1

    # Make the first request
    url = f"{base_url}?page={page}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("Failed to fetch market orders:", response.text)
        return

    orders = response.json()
    all_orders.extend(orders)

    # Check for the total number of pages from the X-Pages header
    total_pages = int(response.headers.get("X-Pages", "1"))
    print(f"Found {total_pages} page(s) of market orders.")

    # Loop over remaining pages (if any)
    for page in range(2, total_pages + 1):
        url = f"{base_url}?page={page}"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch market orders on page {page}:", response.text)
            continue
        orders = response.json()
        all_orders.extend(orders)

    # Write all orders to the marketOrders.json file
    with open(MARKET_FILE, "w") as file:
        json.dump(all_orders, file, indent=2)
    print(f"Fetched a total of {len(all_orders)} market orders across {total_pages} page(s).")

def load_market_orders():
    try:
        with open(MARKET_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print("Market data file not found. Please fetch market orders first.")
        return None

# ======================
# Data loading helpers
# ======================
def load_pi_chains():
    with open(PI_CHAINS_FILE, "r") as f:
        return json.load(f)

def load_unique_items():
    with open(UNIQUE_ITEMS_FILE, "r") as f:
        return json.load(f)

# ======================
# Helper: Convert time string to hours
# ======================
def time_str_to_hours(time_str):
    """Convert an HH:MM:SS time string to hours (as a float)."""
    h, m, s = map(int, time_str.split(":"))
    return h + m / 60.0 + s / 3600.0

# ======================
# Market Price Lookup
# ======================
def get_market_price(item_name, market_data, unique_items, price_type):
    """
    Look up the ESI ID for an item using unique_items (which maps item names to IDs)
    and then search the market_data orders for orders matching that type_id.
    For "maxBuy", only buy orders (is_buy_order True) are considered and the highest price is returned.
    For "minSell", only sell orders (is_buy_order False) are considered and the lowest price is returned.
    """
    item_id = unique_items.get(item_name)
    if item_id is None:
        print(f"Item '{item_name}' not found in unique items.")
        return None

    if price_type == "maxBuy":
        prices = [order["price"] for order in market_data 
                  if order.get("type_id") == item_id and order.get("is_buy_order") == True]
    else:  # assuming price_type == "minSell"
        prices = [order["price"] for order in market_data 
                  if order.get("type_id") == item_id and order.get("is_buy_order") == False]

    if not prices:
        print(f"No market price found for item '{item_name}' (ID: {item_id}) for price type '{price_type}'.")
        return None

    return max(prices) if price_type == "maxBuy" else min(prices)

# ======================
# Profitability Calculation (Normalized per Hour)
# ======================
def calculate_profitability(price_type, station_name):
    if station_name not in STATIONS:
        print("Invalid station selected.")
        return

    market_data = load_market_orders()
    if not market_data:
        print("Market data not available. Please fetch it first.")
        return

    unique_items = load_unique_items()  # mapping: item name -> id
    pi_chains = load_pi_chains()        # keys: "P{level}->OutputItem"
    
    # Group chains by output item name.
    groups = {}
    for key, chain in pi_chains.items():
        try:
            level_str, output_item = key.split("->")
        except ValueError:
            continue
        level = int(level_str[1:])  # remove the leading 'P'
        if output_item not in groups:
            groups[output_item] = []
        groups[output_item].append((level, chain))
    
    # For each output item, choose the chain with the highest P level (i.e. the immediate recipe)
    for output_item, chains in groups.items():
        chosen_level, chosen_chain = max(chains, key=lambda x: x[0])
        output_price = get_market_price(output_item, market_data, unique_items, price_type)
        if output_price is None:
            print(f"Skipping {output_item} because no output price was found.")
            continue

        total_input_cost = 0.0
        # Sum the cost of each input in the chosen chain (skip the "Time" field)
        for input_item, qty in chosen_chain.items():
            if input_item == "Time":
                continue
            input_price = get_market_price(input_item, market_data, unique_items, price_type)
            if input_price is None:
                print(f"Could not find market price for input '{input_item}' in {output_item}.")
                continue
            total_input_cost += input_price * qty

        profit = output_price - total_input_cost
        
        # Normalize profit per hour using the production time from the chain.
        production_time_str = chosen_chain.get("Time")
        if production_time_str:
            production_hours = time_str_to_hours(production_time_str)
            if production_hours > 0:
                normalized_profit = profit / production_hours
            else:
                normalized_profit = None
        else:
            normalized_profit = None

        print(f"Output: {output_item} (chain P{chosen_level})")
        print(f"  Output Price: {output_price} ISK")
        print(f"  Total Input Cost: {total_input_cost} ISK")
        print(f"  Profit per Cycle: {profit} ISK")
        if normalized_profit is not None:
            print(f"  Normalized Profit: {normalized_profit:.2f} ISK/hour")
        else:
            print("  Normalized Profit: N/A (production time missing)")
        print(f"  Production Time: {production_time_str}\n")

# ======================
# GUI Code
# ======================
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
    station_dropdown.set("Beanstar")
    station_dropdown.pack()
    
    auth_button = tk.Button(root, text="Authenticate with EVE", command=get_auth_token)
    auth_button.pack()
    
    fetch_button = tk.Button(root, text="Fetch Market Orders", command=fetch_market_orders)
    fetch_button.pack()
    
    calc_button = tk.Button(root, text="Calculate Profitability",
                            command=lambda: calculate_profitability(price_type_dropdown.get(), station_dropdown.get()))
    calc_button.pack()
    
    root.mainloop()

if __name__ == "__main__":
    create_gui()
