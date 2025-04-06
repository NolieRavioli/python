import csv
from collections import defaultdict

# Adjust these to match your actual filenames:
files = [
    ("asedf", "asdf.csv"),
    ("asdf", "asdf.csv"),
    ("asdf", "asdf.csv")
]

# Decide which column to use as the unique key:
BLUEPRINT_KEY_COLUMN = "Blueprint ID"  # or "Blueprint Name"

# We'll store all rows in a dict: { blueprint_key: [(owner_name, row_dict), ...], ... }
all_rows = defaultdict(list)

# 1. Read all rows from each CSV.
#    We do NOT filter out unowned here, because we want "every item" in the output.
for (char_name, filename) in files:
    with open(filename, mode="r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Keep track of which character/file the row came from (optional).
            # You could also store it in the row itself if you want.
            row["Character"] = char_name

            # Use Blueprint ID (or Name) as the dictionary key.
            key = row[BLUEPRINT_KEY_COLUMN]
            all_rows[key].append(row)

# Decide on the final CSV columns. Must match your CSV structure:
fieldnames = [
    "API ID", "Location ID", "Item ID", "Blueprint ID", "Blueprint Group",
    "Blueprint Name", "Quantity", "Flag ID", "ME", "TE", "Runs", "BP Type",
    "Owned", "Scanned", "Favorite", "Additional Costs", "Character"
]

# Helper function to safely convert ME/TE to int, default to 0 if missing/non-numeric:
def parse_int(value):
    try:
        return int(value)
    except:
        return 0

def pick_best_row(rows_for_this_blueprint):
    owned_rows = [r for r in rows_for_this_blueprint if r["Owned"] != "Unowned"]

    # If nothing is owned, just pick the first row
    if not owned_rows:
        return rows_for_this_blueprint[0]

    # Separate out BPO vs BPC among the owned rows
    bpo_rows = [r for r in owned_rows if r["BP Type"].strip().upper() == "BPO"]
    bpc_rows = [r for r in owned_rows if r["BP Type"].strip().upper() == "BPC"]

    if len(bpo_rows) == 1:
        # Exactly one BPO row, pick it
        return bpo_rows[0]
    elif len(bpo_rows) > 1:
        # Multiple BPO rows -> pick the one with the highest ME+TE
        return max(bpo_rows, key=lambda r: parse_int(r["ME"]) + parse_int(r["TE"]))
    else:
        # No BPO among owned rows => we expect all BPC. But let's check:
        if bpc_rows:
            # If we have one or more BPC rows, pick the one with the highest ME+TE
            return max(bpc_rows, key=lambda r: parse_int(r["ME"]) + parse_int(r["TE"]))
        else:
            # Fallback if somehow we didn't find ANY BPO or BPC.
            # Possibly a weird row has Owned="True" but "BP Type" is missing or invalid.
            # Let's just pick the first owned row or handle differently:
            return owned_rows[0]


# 2. Create the output CSV and write exactly one row per blueprint.
output_filename = "combined_output.csv"
with open(output_filename, mode="w", encoding="utf-8", newline="") as out_f:
    writer = csv.DictWriter(out_f, fieldnames=fieldnames)
    writer.writeheader()

    for blueprint_key, rows in all_rows.items():
        best = pick_best_row(rows)
        writer.writerow(best)

print(f"Done! Wrote merged data to {output_filename}")
