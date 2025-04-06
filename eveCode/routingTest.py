import json
import networkx as nx
import time

ship = {
    'name':'chiron',
    'cargo':1000000,
    'contents':[
        {
            'typeID':44992,
            'quantity':2000,
            'volume':20
        },
        {
            'typeID':44993,
            'quantity':2000,
            'volume':20
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

# Create a directed graph
Gsystems = nx.DiGraph()

# Iterate over each node in the data
for node_id, node_info in All_systems.items():
    node_id = int(node_id)
    Gsystems.add_node(node_id)

    # Add inter-system edges (cost = 2)
    for neighbor in node_info.get('neighbors', []):
        Gsystems.add_edge(node_id, neighbor, weight=1)

def getRoute(source, target):
    try:
        path = nx.dijkstra_path(Gsystems, source, target, weight='weight')
        total_cost = nx.dijkstra_path_length(Gsystems, source, target, weight='weight')
        return total_cost, path  # Return travel cost and path
    except nx.NetworkXNoPath:
        return float('inf'), []  # Return infinite cost if no path exists


# Initialize Market dictionary for buy and sell orders
Market = {}
stationList = [int(_) for _ in All_stations.keys()]
for region in marketData:
    print(region)
    for listing in marketData[region]:
        if listing['location_id'] in stationList:
            if listing['type_id'] not in Market.keys():
                Market[listing['type_id']] = {'buyOrders': [], 'sellOrders': []}
            if listing['is_buy_order']:
                Market[listing['type_id']]['buyOrders'].append(listing)
            else:
                Market[listing['type_id']]['sellOrders'].append(listing)
print('ok')


count = 0
# Now compare buy and sell orders for each item
for item_id, orders in Market.items():
    buy_orders = orders['buyOrders']
    sell_orders = orders['sellOrders']
    
    # Compare every sell order to every buy order for the same item
    for sell_order in sell_orders:
        sell_station = sell_order['location_id']
        sell_price = sell_order['price']
        sell_quant = sell_order['volume_remain']

        for buy_order in buy_orders:
            buy_station = buy_order['location_id']
            buy_price = buy_order['price']
            buy_quant = sell_order['volume_remain']

            # Calculate the profit
            profit = buy_price - sell_price

            if profit > 0:
                count += 1
                getRoute(All_stations[str(sell_station)]['solarSystemID'], All_stations[str(buy_station)]['solarSystemID'])
print(count)
