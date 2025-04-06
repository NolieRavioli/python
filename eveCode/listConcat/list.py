# Suppose you have the contents of List 1 in a file named "list1.txt"
# and the contents of List 2 in a file named "list2.txt".
# Each line in list1.txt is just an item name.
# Each line in list2.txt has an item name followed by a quantity (tab or space separated).

def filter_items(list1_file, list2_file):
    # Read List 1 lines, stripping whitespace
    with open(list1_file, 'r', encoding='utf-8') as f1:
        list1 = [line.strip() for line in f1 if line.strip()]

    # Read List 2 lines, stripping whitespace
    with open(list2_file, 'r', encoding='utf-8') as f2:
        list2 = [line.split('\r')[0].strip() for line in f2 if line.strip()]

    # Parse list2 to extract just the item names (ignore quantities)
    # Assuming each line in List 2 is something like:
    #   "<item_name>\t<quantity>"
    # or
    #   "<item_name>    <quantity>"
    # We can split on tab or whitespace and keep the first part.
    items_in_list2 = set()
    for line in list2:
        # If your lines are separated by a tab, use split('\t').
        # If you're not sure (or it might be spaces), you could do split(maxsplit=1) instead:
        item_name = line.rsplit('\t')[0]  # safest if it's definitely tab-separated
        items_in_list2.add(item_name)
##        print(item_name)
##    exit()

    # Filter out items from List 1 that appear in List 2
    filtered_list1 = [item for item in list1 if item not in items_in_list2]

    # Print or return the filtered list (here we just print)
    for item in filtered_list1:
        print(item)
    print(f'list len: {len(filtered_list1)}')

# Example usage (adjust filenames as needed):
if __name__ == "__main__":
    filter_items("list1.txt", "list2.txt")
    
