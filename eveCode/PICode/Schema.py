import json

with open("schematics.json", "r") as f:
    schematics = json.load(f)

# Now you can work with the data:
for tier, items in schematics.items():
    print("Tier:", tier)
    for schematic in items:
        print("  Output:", schematic["output"])
