import json

def transform_file(input_file, output_file):
    # Load the list of objects from the input file.
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    # Build a dictionary mapping each "name" to its corresponding "id".
    result = {item["name"]: item["id"] for item in data}
    
    # Write the result dictionary to the output file.
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    transform_file("input.json", "output.json")
