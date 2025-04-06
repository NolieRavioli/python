import requests
import json
import pandas as pd
from itertools import islice
from time import sleep
import os
import time

request_limit = 30/300 #requests per seconds. poe2 limits us to 30 in 300


def fetch_currency_data(have, want):
    url = "https://www.pathofexile.com/api/trade2/exchange/poe2/Standard"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
        "Accept": "*/*",
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest"
    }
    body = {
        "query": {
            "status": {"option": "any"},
            "have": have,
            "want": want
        },
        "sort": {"have": "asc"},
        "engine": "new"
    }

    response = requests.post(url, headers=headers, json=body)
    print(f"rate: {response.headers['X-Rate-Limit-Ip']}\nused: {response.headers['X-Rate-Limit-Ip-State']}")

    if response.status_code == 200:
        sleep(request_limit+0.001)
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        sleep(300)
        return None

def parse_currency_data(data):
    listings = data
    table = []

    for listing in listings:
        offers = listing['listing']['offers']
        for offer in offers:
            exchange = offer.get('exchange', {})
            item = offer.get('item', {})
            have = exchange.get('amount')
            want = item.get('amount')
            stock = item.get('stock', 0)
            exchange_currency = exchange.get('currency')
            item_currency = item.get('currency')

            if have and want and exchange_currency and item_currency and stock > 0:
                # Store data including both currencies for sorting/filtering
                table.append({
                    "Have": have,
                    "Want": want,
                    "Rate": float(have) / float(want),
                    "Stock": stock,
                    "Exchange Currency": exchange_currency,
                    "Item Currency": item_currency
                })

    return pd.DataFrame(table)

def find_profitable_trades(data):
    df = parse_currency_data(data)
    
    # Exclude listings where stock is less than the rate
    df = df[df["Stock"] >= df["Rate"]]
    
    # Group by the exchange and item currencies
    grouped = df.groupby(["Exchange Currency", "Item Currency"])

    # List to store the result
    results = []

    for (exchange_currency, item_currency), group in grouped:
        total_stock = group["Stock"].sum()
        five_percent_stock = total_stock * 0.05
        
        # Sort the group by rate (lowest first) and accumulate stock until reaching 5% of total stock
        group = group.sort_values(by="Rate", ascending=True)
        
        accumulated_stock = 0
        selected_trades = []
        
        for _, row in group.iterrows():
            if accumulated_stock < five_percent_stock:
                selected_trades.append(row)
                accumulated_stock += row["Stock"]
            else:
                break
        
        # Calculate the average exchange rate of the selected trades
        if selected_trades:
            avg_rate = sum([trade["Rate"] * trade["Stock"] for trade in selected_trades]) / accumulated_stock
            results.append({
                "Exchange Currency": exchange_currency,
                "Item Currency": item_currency,
                "Average Rate": avg_rate**(-1),
                "Total Stock": total_stock,
                "Selected Volume (5%)": accumulated_stock
            })
    
    return pd.DataFrame(results)

def generate_batches(items, batch_size):
    """Generate consecutive batches from a list."""
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]

def queryData():
    # Define the master lists
    have_items = [
        "chaos", "wisdom", "transmute", "aug", "chance", "alch", "vaal", "regal", "exalted", "divine",
        "annul", "artificers", "mirror", "scrap", "whetstone", "etcher", "bauble", "gcp"
    ]
    want_items = [
        "chaos", "wisdom", "transmute", "aug", "chance", "alch", "vaal", "regal", "exalted", "divine",
        "annul", "artificers", "mirror", "scrap", "whetstone", "etcher", "bauble", "gcp"
    ]

    batch_size = 1
    output = []
    t1 = time.time()

    # Generate all possible combinations of batches for have_items and want_items
    for have_batch in generate_batches(have_items, batch_size):
        for want_batch in generate_batches(want_items, batch_size):
            if want_batch != have_batch:
                print(f"Fetching data for have: {have_batch} and want: {want_batch}")
                data = fetch_currency_data(have_batch, want_batch)
                remaining_seconds = max(0, int(t1 + 4000 - time.time()))
                print(f"{remaining_seconds//3600}h, {remaining_seconds%3600//60}m, {remaining_seconds%60}s remaining".lstrip("0h, ").lstrip("0m, "))
                if data and "result" in data:
                    try:
                        output.extend(data["result"].values())
                    except Exception as e:
                        print(f"Error processing data for {have_batch} and {want_batch}: {e}")
    return output


if __name__ == "__main__":
    if os.path.exists('currency_data.json'):
        with open("currency_data.json", "r") as f:
            all_data = json.load(f)
    else:
        all_data = queryData()
        # Save to JSON file
        with open("currency_data.json", "w") as f:
            json.dump(all_data, f, indent=4)
        print("Data saved to currency_data.json")

    # After collecting all data
    if all_data:
        
        # Get the table with average rates for each exchange pair
        profitable_trades = find_profitable_trades(all_data)
        
        print("\nAverage Exchange Rate for Each Currency Pair:")
        print(profitable_trades)

        # Save the profitable trades table to a file
        with open("profitable_trades.json", "w") as f:
            json.dump(profitable_trades.to_dict(orient="records"), f, indent=4)
        print("Profitable trades saved to profitable_trades.json")
