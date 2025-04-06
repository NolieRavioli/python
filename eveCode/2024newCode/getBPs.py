neededBps = '''Brutix Blueprint
Cyclone Blueprint
Drake Blueprint
Drekavac Blueprint
Ferox Blueprint
Gnosis Blueprint
Harbinger Blueprint
Hurricane Blueprint
Myrmidon Blueprint
Naga Blueprint
Oracle Blueprint
Prophecy Blueprint
Talos Blueprint
Tornado Blueprint
Abaddon Blueprint
Apocalypse Blueprint
Apocalypse Imperial Issue Blueprint
Armageddon Blueprint
Dominix Blueprint
Hyperion Blueprint
Leshak Blueprint
Maelstrom Blueprint
Marshal Blueprint
Megathron Blueprint
Megathron Federate Issue Blueprint
Praxis Blueprint
Raven Blueprint
Rokh Blueprint
Scorpion Blueprint
Tempest Blueprint
Thunderchild Blueprint
Typhoon Blueprint
Rorqual Blueprint
Archon Blueprint
Chimera Blueprint
Nidhoggur Blueprint
Thanatos Blueprint
Arbitrator Blueprint
Augoror Blueprint
Bellicose Blueprint
Blackbird Blueprint
Celestis Blueprint
Chameleon Blueprint
Enforcer Blueprint
Etana Blueprint
Exequror Blueprint
Fiend Blueprint
Guardian-Vexor Blueprint
Laelaps Blueprint
Maller Blueprint
Moa Blueprint
Monitor Blueprint
Moracha Blueprint
Omen Blueprint
Osprey Blueprint
Rabisu Blueprint
Rodiva Blueprint
Rupture Blueprint
Scythe Blueprint
Stormbringer Blueprint
Thorax Blueprint
Tiamat Blueprint
Vangel Blueprint
Victor Blueprint
Victorieux Luxury Yacht Blueprint
Algose Blueprint
Cormorant Blueprint
Kikimora Blueprint
Sunesis Blueprint
Talwar Blueprint
Thrasher Blueprint
Moros Blueprint
Naglfar Blueprint
Phoenix Blueprint
Revelation Blueprint
Zimtra Blueprint
Apostle Blueprint
Dagon Blueprint
Lif Blueprint
Loggerhead Blueprint
Minokawa Blueprint
Ninazu Blueprint
Avalanche Blueprint
Bowhead Blueprint
Charon Blueprint
Fenrir Blueprint
Obelisk Blueprint
Providence Blueprint
Caedes Blueprint
Cambion Blueprint
Chremoas Blueprint
Executioner Blueprint
Hydra Blueprint
Imp Blueprint
Inquisitor Blueprint
Magnate Blueprint
Malice Blueprint
Metamorphosis Blueprint
Pacifier Blueprint
Raiju Blueprint
Skybreaker Blueprint
Tormentor Blueprint
Virtuoso Blueprint
Whiptail Blueprint
Bestower Blueprint
Hoarder Blueprint
Miasmos Amastris Edition Blueprint
Miasmos Quafe Ultra Edition Blueprint
Miasmos Quafe Ultramarine Edition Blueprint
Noctis Blueprint
Sigil Blueprint
Squall Blueprint
Orca Blueprint
Porpoise Blueprint
Covetor Blueprint
Procurer Blueprint
Retriever Blueprint
Apotheosis Blueprint
Boobook Blueprint
Council Diplomatic Shuttle Blueprint
InterBus Shuttle Blueprint
Leopard Blueprint
Aeon Blueprint
Hel Blueprint
Nyx Blueprint
Revenant Blueprint
Vendetta Blueprint
Wyvern Blueprint
Avatar Blueprint
Azariel Blueprint
Erebus Blueprint
Komodo Blueprint
Leviathan Blueprint
Molok Blueprint
Ragnarok Blueprint
Vanquisher Blueprint'''

import requests
import json

blueprint_list = neededBps.split("\n")

# Step 2: URL for resolving names to item IDs
nameUrl = "https://esi.evetech.net/latest/universe/ids/"

# Send POST request to get item IDs
nameResponse = requests.post(nameUrl, json=blueprint_list)
if nameResponse.status_code == 200:
    name_data = nameResponse.json()
    item_ids = [item['id'] for item in name_data['inventory_types']]
    print(item_ids)

    # Step 3: Fetch cheapest market prices for each blueprint
    cheapest_prices = {}
    for typeId in item_ids:
        count = 0
        rimnrt = True
        market_url = f"https://evetycoon.com/api/v1/market/orders/{typeId}"
        while rimnrt:
            marketResponse = requests.get(market_url)
            if marketResponse.status_code == 200:
                rimnrt = False
                market_data = marketResponse.json()['orders']
                sell_orders = [order for order in market_data if order['isBuyOrder'] == False]
                if sell_orders:
                    cheapest_price = min(order['price'] for order in sell_orders)
                    cheapest_prices[typeId] = [cheapest_price,set()]
                    for order in sell_orders:
                        location = order['locationId']
                        sys = order['systemId']
                        if order['price'] < float(cheapest_price*1.05):
                            cheapest_prices[typeId][1].add(sys)
                    #print(f"{typeId}: {cheapest_prices[typeId][0]} ISK")
                    #print(cheapest_prices[typeId][1])
                else:
                    cheapest_prices[typeId] = None
            else:
                count += 1
                if count > 5:
                    print(f'failed {typeId}')
                    rimnrt = False
        

    # Print the results
    for blueprint, item_id in zip(blueprint_list, item_ids):
        price = cheapest_prices.get(item_id, None)
        if price:
            price = price[0]
            cheapest_prices[item_id][1] = list(cheapest_prices[item_id][1])
            print(f"{blueprint}: {price} ISK")
    with open('bp.json','w') as f:
        json.dump(cheapest_prices, f, indent=4)
    
else:
    print("Failed to fetch item IDs. Check your API endpoint and payload.")
