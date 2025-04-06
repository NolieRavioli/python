import os
import json
import yaml

# Define file paths
bp_list_path = r'list1.txt'
sde_path = r'C:\Users\nolan\Downloads\fsd\types.yaml'
output_path = r'list1_with_prices.txt'

def load_sde_base_prices(sde_path):
    """Load SDE invTypes.yaml and return a dictionary mapping typeID to base price."""
    with open(sde_path, 'r', encoding='utf-8') as file:
        sde_data = yaml.safe_load(file)
    print('loaded yaml safely')
    base_prices = {}
    for itemId in sde_data:
        type_name = sde_data[itemId]["name"]["en"]
        base_price = sde_data[itemId].get("basePrice", float('inf'))
        if type_name:
            base_prices[type_name] = [base_price,itemId]
    
    return base_prices

def update_bp_list(bp_list_path, base_prices, output_path):
    """Update list1.txt with base prices."""
    with open(bp_list_path, 'r', encoding='utf-8') as bp_file, open(output_path, 'w', encoding='utf-8') as out_file:
        out_file.write('name,bpId,basePrice\n')
        for line in bp_file:
            bp_name = line.strip()
            base_price = base_prices[bp_name][0]
            bpId = base_prices[bp_name][1]
            out_file.write(f"{bp_name},{bpId},{base_price}\n")

def main():
    base_prices = load_sde_base_prices(sde_path)
    update_bp_list(bp_list_path, base_prices, output_path)
    print(f"Updated list with base prices saved to: {output_path}")

if __name__ == "__main__":
    main()
