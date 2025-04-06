import json
import networkx as nx
import time
import concurrent.futures

# Ship data (included for future usage)
ship = {
    'name': 'chiron',
    'cargo': 1000000,
    'contents': [
        {
            'typeID': 44992,
            'quantity': 2000,
            'volume': 20
        },
        {
            'typeID': 44993,
            'quantity': 2000,
            'volume': 20
        }
    ]
}

# Load the JSON data from the file
with open('testsysData.json', 'r') as file:
    All_systems = json.load(file)

with open('teststationData.json', 'r') as file:
    All_stations = json.load(file)

with open('market_orders.json', 'r') as file:
    marketData = json.load(file)

# Create a directed graph for systems
Gsystems = nx.DiGraph()

# Build the graph: systems connected by stargates (inter-system)
for node_id, node_info in All_systems.items():
    node_id = int(node_id)
    Gsystems.add_node(node_id)
    for neighbor in node_info.get('neighbors', []):
        Gsystems.add_edge(node_id, neighbor, weight=1)

# Function to get the shortest path between systems and calculate travel cost
def getRoute(source, target):
    try:
        path = nx.dijkstra_path(Gsystems, source, target, weight='weight')
        total_cost = nx.dijkstra_path_length(Gsystems, source, target, weight='weight')
        return total_cost, path  # Return travel cost and path
    except nx.NetworkXNoPath:
        return float('inf'), []  # Infinite cost if no path exists

# Build the market data into buy and sell orders by item
def buildMarketData():
    Market = {}
    stationList = [int(_) for _ in All_stations.keys()]
    for region in marketData:
        for listing in marketData[region]:
            if listing['location_id'] in stationList:
                if listing['type_id'] not in Market:
                    Market[listing['type_id']] = {'buyOrders': [], 'sellOrders': []}
                if listing['is_buy_order']:
                    Market[listing['type_id']]['buyOrders'].append(listing)
                else:
                    Market[listing['type_id']]['sellOrders'].append(listing)
    return Market

# Function to compare buy and sell orders for an item
def compare_orders_for_item(item_id, orders):
    buy_orders = orders['buyOrders']
    sell_orders = orders['sellOrders']
    count = 0
    
    # Compare every sell order to every buy order for the same item
    for sell_order in sell_orders:
        sell_station = sell_order['location_id']
        sell_price = sell_order['price']
        sell_quant = sell_order['volume_remain']

        for buy_order in buy_orders:
            buy_station = buy_order['location_id']
            buy_price = buy_order['price']
            buy_quant = buy_order['volume_remain']

            # Calculate the profit
            profit = buy_price - sell_price

            if profit > 0:
                count += 1
                getRoute(All_stations[str(sell_station)]['solarSystemID'], All_stations[str(buy_station)]['solarSystemID'])
    
    return count

# Function to compare a chunk of market items (used for threading)
def process_market_chunk(market_chunk):
    count = 0
    for item_id, orders in market_chunk.items():
        count += compare_orders_for_item(item_id, orders)
    return count

# Function to calculate total orders (buy + sell) per item
def calculate_item_weights(Market):
    item_weights = {}
    for item_id, orders in Market.items():
        total_orders = len(orders['buyOrders']) + len(orders['sellOrders'])
        item_weights[item_id] = total_orders
    return item_weights

# Function to split the market into weighted chunks
def split_market_weighted(Market, item_weights, num_chunks=20):
    # Sort items by their total order count in descending order
    sorted_items = sorted(item_weights.items(), key=lambda x: x[1], reverse=True)
    
    chunks = [{} for _ in range(num_chunks)]  # Create empty chunks
    chunk_weights = [0] * num_chunks  # Track the total weight of each chunk

    # Distribute items to chunks in a balanced way
    for item_id, weight in sorted_items:
        # Find the chunk with the least total weight and add the item to that chunk
        min_chunk_idx = chunk_weights.index(min(chunk_weights))
        chunks[min_chunk_idx][item_id] = Market[item_id]
        chunk_weights[min_chunk_idx] += weight

    return chunks

# Main program
if __name__ == '__main__':
    # Build the market data
    Market = buildMarketData()
    print("Market data loaded and organized.")

    # Calculate item weights (total number of orders per item)
    item_weights = calculate_item_weights(Market)

    # Split the market into weighted chunks based on the number of orders
    market_chunks = split_market_weighted(Market, item_weights, num_chunks=20)

    # Thread-safe counter for profitable trades
    total_count = 0

    # Use ThreadPoolExecutor to process market chunks in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_to_chunk = {executor.submit(process_market_chunk, chunk): chunk for chunk in market_chunks}
        
        for future in concurrent.futures.as_completed(future_to_chunk):
            try:
                result = future.result()
                total_count += result
                print(f"Completed chunk with {result} profitable trades.")
            except Exception as exc:
                print(f"Generated an exception: {exc}")

    # Output the total count of profitable trades
    print(f"Total profitable trades found: {total_count}")
