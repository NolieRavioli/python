import yaml
from yaml import CLoader as Loader
import json
import csv
import os

'region.yaml'


sec = -2
# Initialize systemData as empty dict
systemData = {}

def getStargates(stargates_data):
    """Extract stargate information from the data and return a formatted structure."""
    out = {}
    for stargateID in stargates_data:
        out[stargateID] = {
            'stargateID': stargateID,
            'destination': stargates_data[stargateID]['destination'],  # Destination stargate ID
            'position': stargates_data[stargateID]['position'],  # Position in the system
            'typeID': stargates_data[stargateID]['typeID']  # Type ID of the stargate
            }
    return out

def walkTheUniverse():
    """Traverse the directory structure to build systemData with systems."""
    root_dir = r'C:\Users\Nolan\Desktop\Eve Online Code\eve'

    # Walk through all subdirectories and collect system data
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename == 'region.yaml':
                filepath = os.path.join(dirpath, filename)
                with open(filepath, 'r') as file:
                    try:
                        data = yaml.load(file,Loader=Loader)
                        regionID = data['regionID']
                    except yaml.YAMLError as exc:
                        print(f"Error parsing YAML file {filepath}: {exc}")
                        continue
                print(dirpath[len(root_dir) + 1:].split(os.sep)[0], f'{(100*len(systemData)/5432):.2f}% done building universe')
            elif filename == 'constellation.yaml':
                pass#print(dirnames)
            else:
                filepath = os.path.join(dirpath, filename)
                with open(filepath, 'r') as file:
                    try:
                        data = yaml.load(file,Loader=Loader)
                    except yaml.YAMLError as exc:
                        print(f"Error parsing YAML file {filepath}: {exc}")
                        continue
                
                security = data['security']
                system_name = os.path.basename(dirpath)
                parts = dirpath[len(root_dir) + 1:].split(os.sep)
                region = parts[0]
                consta = parts[1]
                systemName = parts[2]
                solarSystemID = data['solarSystemID']
                stargates = getStargates(data['stargates'])  # Extract stargates using updated function

                # Add system data only if it's high-security
                if security >= 0.45 or 1:
                    systemData[solarSystemID] = {
                        'name': systemName,
                        'security': security,
                        'cost_indices': {},
                        'regionID': regionID,
                        'region': region,
                        'constellation': consta,
                        'neighbors': [],  # This will store neighboring systems
                        'stargates': stargates  # Now contains structured stargate data
                    }
                    for stargate in systemData[solarSystemID]['stargates']:
                        destStargate = systemData[solarSystemID]['stargates'][stargate]['destination']
                        for destSystemID in systemData:
                            if destStargate in systemData[destSystemID]['stargates'].keys():
                                systemData[solarSystemID]['neighbors'].append(destSystemID)
                                systemData[destSystemID]['neighbors'].append(solarSystemID)
                                systemData[solarSystemID]['stargates'][stargate]['destinationSystem'] = destSystemID
                                systemData[destSystemID]['stargates'][destStargate]['destinationSystem'] = solarSystemID


walkTheUniverse()

with open('industryCost.json', 'r') as file:
    indy = json.load(file)

print(len(indy))

for indysystem in indy:
    for activity in indysystem['cost_indices']:
        try:
            systemData[indysystem['solar_system_id']]['cost_indices'][activity['activity']] = activity['cost_index']
        except Exception as e:
            pass
open('systemData.json', 'w').write(json.dumps(systemData, indent=4))

