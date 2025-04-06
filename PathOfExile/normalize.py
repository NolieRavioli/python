import json

with open("profitable_trades.json", "r") as f:
    all_data = json.load(f)

exPrices = {}
exPrices['exalted'] = 1
for combo in all_data:
    if combo['Exchange Currency'] == "exalted":
        exPrices[combo['Item Currency']] = combo['Average Rate']

norm = {}
for combo in all_data:
    if combo['Exchange Currency'] != "exalted":
        if combo['Exchange Currency'] not in norm.keys():
            norm[combo['Exchange Currency']] = {}
        else:
            try:
                exRate = (exPrices[combo['Item Currency']] / exPrices[combo['Exchange Currency']])
            except KeyError:
                pass
            norm[combo['Exchange Currency']][combo['Item Currency']] = combo['Average Rate'] / exRate - 1

with open('mmmhmm.json','w') as f:
    json.dump(norm, f, indent=4)
