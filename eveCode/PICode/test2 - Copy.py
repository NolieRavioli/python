import json

# --- Time conversion helpers ---

def time_str_to_seconds(t_str):
    """Convert a HH:MM:SS string to seconds."""
    h, m, s = map(int, t_str.split(":"))
    return h * 3600 + m * 60 + s

def seconds_to_time_str(seconds):
    """Convert seconds to a HH:MM:SS string."""
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

# --- Schematic lookup and chain expansion functions ---

def tier_to_num(tier_str):
    """Convert a tier string (e.g. 'Tier 4') to its numeric value."""
    mapping = {
        "Tier 4": 4,
        "Tier 3": 3,
        "Tier 2": 2,
        "Tier 1": 1,
        "Tier 0": 0
    }
    return mapping.get(tier_str, None)

def build_lookup(schematics_data):
    """
    Build a dictionary that maps (numeric tier, product name) to its schematic.
    Only schematics for products produced in Tier 1–Tier 4 are included.
    """
    lookup = {}
    for tier in ["Tier 4", "Tier 3", "Tier 2", "Tier 1"]:
        if tier not in schematics_data:
            continue
        for schematic in schematics_data[tier]:
            product_name = schematic["output"]["item"]
            product_tier = tier_to_num(schematic["output"]["tier"])
            lookup[(product_tier, product_name)] = schematic
    return lookup

def expand_chain(product_name, product_tier, stop_tier, lookup):
    """
    Recursively expand the production chain for a product.
    
    Parameters:
      product_name (str): Name of the product.
      product_tier (int): Tier at which the product is produced.
      stop_tier (int): Do not expand inputs that are produced at or below this tier.
      lookup (dict): Mapping of (tier, product name) -> schematic.
    
    Returns:
      A dictionary mapping ingredient names to the quantity needed per one unit of output.
    
    If the product’s tier is <= stop_tier, it is considered terminal.
    """
    if product_tier <= stop_tier:
        return { product_name: 1.0 }
    
    key = (product_tier, product_name)
    if key not in lookup:
        return { product_name: 1.0 }
    
    schematic = lookup[key]
    out_qty = schematic["output"]["quantity"]
    factor = 1.0 / out_qty  # factor to compute input per one unit of product
    result = {}
    
    for inp in schematic["inputs"]:
        qty = inp["quantity"] * factor
        # If an input does not list a tier, assume it’s a raw resource (Tier 0)
        inp_tier = tier_to_num(inp["tier"]) if "tier" in inp else 0
        
        if inp_tier > stop_tier:
            # Recursively expand this input.
            subchain = expand_chain(inp["item"], inp_tier, stop_tier, lookup)
            for sub_item, sub_qty in subchain.items():
                result[sub_item] = result.get(sub_item, 0) + sub_qty * qty
        else:
            result[inp["item"]] = result.get(inp["item"], 0) + qty
    return result

# --- Main script ---

def main():
    # Read schematics from 'schematics.json'
    with open("schematics.json", "r") as f:
        schematics_data = json.load(f)
    
    lookup = build_lookup(schematics_data)
    pi_chains = {}
    
    # Process every product schematic from Tier 1–Tier 4.
    for tier_str in ["Tier 4", "Tier 3", "Tier 2", "Tier 1"]:
        if tier_str not in schematics_data:
            continue
        
        for schematic in schematics_data[tier_str]:
            product_name = schematic["output"]["item"]
            product_tier = tier_to_num(schematic["output"]["tier"])
            
            # Compute production time per unit:
            # Convert the cycle time (e.g. "01:00:00") to seconds, then divide by output quantity.
            cycle_time_seconds = time_str_to_seconds(schematic["cycleTime"])
            output_qty = schematic["output"]["quantity"]
            time_per_unit_sec = cycle_time_seconds / output_qty
            time_per_unit_str = seconds_to_time_str(int(time_per_unit_sec))
            
            # Loop over stop_tiers. Adjust the range as needed.
            # Here we generate keys for stop_tier from 0 to product_tier - 1.
            for stop_tier in range(product_tier):
                chain = expand_chain(product_name, product_tier, stop_tier, lookup)
                # Add the time field (which is always that of the final product’s schematic)
                chain["Time"] = time_per_unit_str
                key = f"P{stop_tier}->{product_name}"
                # Optionally, round the ingredient quantities for clarity.
                chain = { k: (round(v, 2) if k != "Time" else v) for k, v in chain.items() }
                pi_chains[key] = chain

    # Write the production-chain data (with time) to 'pi_chains.json'
    with open("pi_chains.json", "w") as f:
        json.dump(pi_chains, f, indent=4)
    
    print("pi_chains.json has been generated.")

if __name__ == "__main__":
    main()
