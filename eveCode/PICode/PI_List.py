import json
import re

def clean_string(s):
    """
    Remove the unwanted substrings from a given string.
    - Removes " Raw Resource" anywhere in the string.
    - Removes the prefix "P#->" if it occurs at the start, where # is 0, 1, 2, or 3.
    """
    # Remove " Raw Resource"
    s = s.replace(" Raw Resource", "")
    # Remove the "P#->" prefix using a regular expression.
    s = re.sub(r'^P[0-3]->', '', s)
    return s

def main():
    # Load the production-chain data from pi_chains.json.
    with open("pi_chains.json", "r") as f:
        pi_chains = json.load(f)
    
    # Create a set to hold unique names.
    unique_items = set()
    
    # Iterate over each production-chain entry.
    for chain_key, chain in pi_chains.items():
        # Clean the outer key (production-chain name) and add it.
        cleaned_chain_key = clean_string(chain_key)
        unique_items.add(cleaned_chain_key)
        
        # Iterate over each item within the chain.
        for item in chain:
            # Skip the "Time" field.
            if item == "Time":
                continue
            # Clean the ingredient name and add it.
            cleaned_item = clean_string(item)
            unique_items.add(cleaned_item)
    
    # Create a sorted list of unique items.
    unique_list = sorted(unique_items)
    
    # Write the unique items to a JSON file.
    with open("unique_items.json", "w") as f:
        json.dump(unique_list, f, indent=4)
    
    print(unique_list)

if __name__ == "__main__":
    main()
