import os
import difflib
from collections import defaultdict

steamappsFolder = r'C:\Program Files (x86)\Steam\steamapps'
carrier_command_data = r'\rom_0'

def workshop(workshopid):
    return os.path.join(steamappsFolder, fr'workshop\content\1489630\{workshopid}\content')

mods = {
    # Your mod entries here...
    # Later Mod Entries will override earlier mod entries. Keep this in mind.
    "IncreaseRadarRange": workshop("2849827250"),
    "Lubricant": workshop("2980659880"),
    "UIEnhancer": workshop("2761300794"),
    "CallsignsForVehicles": workshop("2817920223"),
    "SpecializedChassisV": workshop("2812565529"),
    "Albatross AWACS": workshop("2891723169"),
    "DynamicAirMap": workshop("3000126914"),
    "RWR": workshop("2983661961"),
    "HelmControl": workshop("2949343185"),
    "CapitanControl": workshop("2824746567"),
    "CarrierVLS": workshop("2985511922"),
    "CaptUnicornMod": workshop("3018266301"),
    "FlyableJets": workshop("2828095394"),
    "BlueBridgeLight": workshop("2871231885")
}

base_folder = os.path.join(steamappsFolder, r'common\Carrier Command 2' + carrier_command_data)

def compare_and_output(file1_path, file2_path):
    with open(file1_path, 'r', encoding='utf-8') as file1:
        file1_lines = file1.readlines()
    with open(file2_path, 'r', encoding='utf-8') as file2:
        file2_lines = file2.readlines()
    diff = difflib.unified_diff(file1_lines, file2_lines, fromfile=file1_path, tofile=file2_path, n=2)
    return list(diff)

# To store changes by file, line number, and mod name
changes_by_file_and_line = defaultdict(lambda: defaultdict(list))

# Initialize a set to keep track of processed file paths
processed_file_paths = {}

for mod_name, mod_folder in mods.items():
    for root, _, files in os.walk(mod_folder):
        for file in files:
            # Skip .txtr files and files in the "textures" folder
            if (not file.lower().endswith(('.txtr', '.mesh'))) and 'textures' not in root.lower() and 'meshes' not in root.lower():
                base_file_path = os.path.join(base_folder, os.path.relpath(os.path.join(root, file), mod_folder))
                mod_file_path = os.path.join(root, file)
                diff = compare_and_output(base_file_path, mod_file_path)
                for line in diff:
                    if line.startswith('@@'):
                        line_info = line.split(' ')
                        line_number = int(line_info[1][1:].split(',')[0])
                    elif (line.startswith('-') or line.startswith('+')) and not (line.startswith('---') or line.startswith('+++')):
                        changes_by_file_and_line[(base_file_path, line_number)][mod_name].append(line)
                        if base_file_path not in processed_file_paths.keys():
                            processed_file_paths[base_file_path] = []
                        if mod_name not in processed_file_paths[base_file_path]:
                            processed_file_paths[base_file_path].append(mod_name)


with open('output3.txt', 'w') as outputFile2:
    for file_path in processed_file_paths:
        outputFile2.write(file_path.split(r'C:\Program Files (x86)\Steam\steamapps\common\Carrier Command 2\rom_0')[1][1:] + '\n')
        mods_that_changed = ', '.join(processed_file_paths[file_path])
        outputFile2.write(mods_that_changed)
        outputFile2.write('\n\n')

with open('output.txt', 'w') as outputFile:
    for mod_name, mod_folder in mods.items():
        print(mod_name)
        outputFile.write(f"Differences between Base and {mod_name} {mod_folder}\n")
        for root, _, files in os.walk(mod_folder):
            for file in files:
                if (not file.lower().endswith(('.txtr', '.mesh'))) and 'textures' not in root.lower() and 'meshes' not in root.lower():
                    base_file_path = os.path.join(base_folder, os.path.relpath(os.path.join(root, file), mod_folder))
                    mod_file_path = os.path.join(root, file)
                    outputFile.write(f"File: {os.path.relpath(mod_file_path, mod_folder)}\n")
                    for line in compare_and_output(base_file_path, mod_file_path):
                        if line.startswith("@@"):
                            outputFile.write('\n'+line)
                        else:
                            outputFile.write(line)
                    outputFile.write('\n\n')

print("done")

file_changes = defaultdict(lambda: defaultdict(list))

with open('output.txt', 'r') as f:
    merge_changes = f.readlines()

for line in merge_changes:
    if (line.startswith('-') or line.startswith('+')) and not (line.startswith('---') or line.startswith('+++')):
        file_changes[current_file][current_line].append(line)
    elif line.startswith("File: "):
        current_file = line.strip().split(' ')[1]
    elif line.startswith('@@'):
        current_line = abs(int(line.split(' ')[1].split(',')[0]))

# Sort the diff headers by starting line number
sorted_changes = {}
for filepath, line_changes in file_changes.items():
    sorted_lines = sorted(line_changes.keys())  # Sort line numbers
    sorted_headers = [(line, line_changes[line]) for line in sorted_lines]
    sorted_changes[filepath] = sorted_headers

# Output the sorted diff headers
out = ""
out1 = ''
for filepath, headers in sorted_changes.items():
    out += filepath+'\n'
    out1 += filepath + '\n'
    for line_number, header in headers:
        out += f'Line {line_number}\n'
        out1 += f'Line {line_number}\n'
        for line in header:
            out += line
            out1 += line[1:] if line[:1] == '+' else ''
    out += '\n'
    out1 += '\n'

with open('output2.txt', 'w') as f:
    f.write(out)

with open('output1.txt', 'w') as f:
    f.write(out1)
