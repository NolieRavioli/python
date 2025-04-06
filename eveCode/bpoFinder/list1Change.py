import yaml
import csv

# Files
INPUT_FILE = "list1.txt"               # Your input with "Blueprint Name\tPrice"
OUTPUT_FILE = "list1_with_prices.txt"  # CSV output
TYPES_FILE = "types.yaml"              # Local SDE file containing type data

def main():
    # --------------------------------------------------------
    # 1) Load 'types.yaml' and build name -> typeID dictionary
    #    The SDE file typically has structure:
    #      {
    #        35834: {
    #          'name': {'en': 'Keepstar Blueprint', ...},
    #          'groupID': 485,
    #          ...
    #        },
    #        12345: {...},
    #        ...
    #      }
    # --------------------------------------------------------
    with open(TYPES_FILE, "r", encoding="utf-8") as f:
        all_types = yaml.safe_load(f)

    name_to_id = {}
    for type_id, info in all_types.items():
        # Typically 'info' has a 'name' key with multiple locales: {'en': 'Keepstar Blueprint', 'de': ...}
        if isinstance(info, dict):
            if "name" in info and isinstance(info["name"], dict):
                en_name = info["name"].get("en", None)
                if en_name:
                    # We'll map "Keepstar Blueprint" -> 35834, etc.
                    name_to_id[en_name] = type_id

    # --------------------------------------------------------
    # 2) Read 'list1.txt' lines: "Blueprint Name\tBest Price"
    # --------------------------------------------------------
    blueprint_entries = []
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = line.split('\t')
            if len(parts) < 2:
                continue  # skip malformed lines

            bp_name = parts[0].strip()
            bp_price_raw = parts[1].strip()

            # Remove commas from the price, e.g. "700,000,000,000.00" -> "700000000000.00"
            bp_price_clean = bp_price_raw.replace(",", "")

            # Store the cleaned-up name and price
            blueprint_entries.append((bp_name, bp_price_clean))

    # --------------------------------------------------------
    # 3) Write out a CSV: name,bpId,bestPrice
    # --------------------------------------------------------
    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as outfile:
        writer = csv.writer(outfile)
        # CSV header row
        writer.writerow(["name", "bpId", "bestPrice"])

        for bp_name, bp_price_str in blueprint_entries:
            # Lookup the blueprint ID in our dictionary; if missing, use an empty string
            bp_id = name_to_id.get(bp_name, "")
            writer.writerow([bp_name, bp_id, bp_price_str])

    print(f"Done! Output written to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
