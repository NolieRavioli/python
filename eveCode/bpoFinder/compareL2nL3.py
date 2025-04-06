import re

def clean_item_name(item_name):
    """Remove quantity prefixes like '2 x ' from item names."""
    return re.sub(r'^\d+ x ', '', item_name).strip()

def load_item_names(filename):
    """Load and clean item names from a file."""
    item_names = set()
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if parts:  # Ensure line is not empty
                item_names.add(clean_item_name(parts[0]))  # Only first column
    return item_names

# Load and clean item names
list2_items = load_item_names('list2.txt')
list3_items = load_item_names('list3.txt')

# Find items in list3 that are not in list2
difference = list3_items - list2_items

# Output results
output_file = "difference.txt"
with open(output_file, 'w', encoding='utf-8') as f:
    for item in sorted(difference):
        f.write(item + '\n')

print(f"Items in list3 but not in list2 saved to: {output_file}")
