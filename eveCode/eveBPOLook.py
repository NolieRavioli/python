import json

def main():
    # 1) Load the JSON data
    with open("locationItems.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        # New format:
        # [
        #   {
        #     "locationId": 60011779,
        #     "locationName": "Unknown 60011779",
        #     "systemId": 30000139,
        #     "jumpsFromStart": 17,
        #     "totalCost": 92532011.0,
        #     "blueprints": [
        #       {"blueprintName": "Rocket Launcher I Blueprint", "blueprintId": 10630, "basePrice": 30000.0},
        #       {"blueprintName": "EM Coating I Blueprint", "blueprintId": 1204, "basePrice": 49740.0},
        #       ...
        #     ]
        #   },
        #   ...
        # ]

    # 2) Rank by how many unique BPOs each location has
    #    Sort locations by the count of blueprints (descending)
    location_rank = sorted(data, key=lambda entry: len(entry["blueprints"]), reverse=True)

    # 3) Display the top 20 locations
    print("\nTop 20 locations by number of BPOs sold (within ISK limit):\n")
    for i, entry in enumerate(location_rank[:20], start=1):
        print(f"{i}. {entry['locationName']} (ID: {entry['locationId']}) - BPO count: {len(entry['blueprints'])}")

    # 4) Prompt user for a locationId to show full list of BPOs
    while True:
        loc_input = input("\nEnter a location ID to see its BPOs (or 'q' to quit): ").strip()
        if loc_input.lower() == 'q':
            break

        try:
            loc_id = int(loc_input)
        except ValueError:
            print("Invalid input. Please enter a numeric location ID.")
            continue

        # Find the location in the dataset
        selected_location = next((entry for entry in data if entry["locationId"] == loc_id), None)
        
        if not selected_location:
            print(f"No data found for location ID '{loc_id}'.")
        else:
            print(f"\nBlueprints at {selected_location['locationName']} (ID: {selected_location['locationId']}):")
            for bp in selected_location["blueprints"]:
                print(f"- {bp['blueprintName']} (ID: {bp['blueprintId']}, Base Price: {bp['basePrice']})")
            print()

if __name__ == "__main__":
    main()
