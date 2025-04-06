import os
import json
import yaml

# Define file paths
bp_list_path = 'list1.txt'
bps = 'blueprints.yaml'
sde_path = 'types.yaml'
groups = 'marketGroups.yaml'
output_path = 'list1_with_prices.txt'

print('loading yaml')
with open(bps, 'r', encoding='utf-8') as file:
    bps_data = yaml.safe_load(file)
print('33% done')
with open(groups, 'r', encoding='utf-8') as file:
    market_groups =  yaml.safe_load(file)
print('67% done')
with open(sde_path, 'r', encoding='utf-8') as file:
    sde_data = yaml.safe_load(file)
print('done')

groups = set([2])
def discover(groups):
    for group in market_groups:
        try:
            parent = market_groups[group]['parentGroupID']
            if parent in groups:
                groups.add(group)
        except KeyError:
            pass
    return groups

gLen = 1
groups = discover(groups)
while gLen != len(groups):
    gLen = len(groups)
    groups = discover(groups)

for itemId in bps_data:
    #print(itemId)
    activities = list(bps_data[itemId]['activities'].keys())
    #print(activities)
    if 'manufacturing' in activities:
        if 'products' in list(bps_data[itemId]['activities']["manufacturing"].keys()):
            try:
                bp = sde_data[itemId]["name"]["en"]
                #product = sde_data[bps_data[itemId]["activities"]["manufacturing"]["products"][0]["typeID"]]["name"]["en"]
                if "marketGroupID" in list(sde_data[bps_data[itemId]["activities"]["manufacturing"]["products"][0]["typeID"]].keys()):
                    marketGroupID = sde_data[itemId]["marketGroupID"]
                    if marketGroupID in groups:
                        price = sde_data[itemId]['basePrice']
                        print(f'{bp},{itemId},{price}')
                    
            except KeyError:
                pass #print(itemId)
