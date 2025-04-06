import yaml
import json
import os

highsec = 0.45
warpSpeed = 95  # ly/sec idk
enterWarp = 45.22  # seconds
autopilotExit = 283.54  # seconds
manualexit = 22.1  # seconds
stationUndock = 45.0  # seconds
warpToStargate = 50.3  # seconds
starGateAnimation = 20.0  # seconds

systemDataStruct = {
    30000142: {  # Jita System ID
        'regionID': 10000002,  # The Forge
        'constellation': 'Kimotoro',
        'stations': [60003760, 60003761, 60003762],  # Station IDs within the system
        'stargates': [
            {'stargateID': 60003433, 'destinationSystem': 30000144, 'destinationStargateID': 60003466},
            {'stargateID': 60003434, 'destinationSystem': 30000145, 'destinationStargateID': 60003510}
        ]
    },
    30000144: {  # Another system
        'regionID': 10000003,
        'constellation': 'Kimotoro',
        'stations': [60003455, 60003456],
        'stargates': [
            {'stargateID': 60003466, 'destinationSystem': 30000142, 'destinationStargateID': 60003433}
        ]
    }
}

stationDataStruct = {
    60003760: {  # Caldari Navy Assembly Plant in Jita
        'solarSystemID': 30000142,  # Jita System ID
        'buyOrders': [
            {'item': 'Tritanium', 'price': 4.1, 'quantity': 100000},
            {'item': 'Plex', 'price': 2800000.0, 'quantity': 5}
        ],
        'sellOrders': [
            {'item': 'Tritanium', 'price': 4.3, 'quantity': 1000000},
            {'item': 'Plex', 'price': 3000000.0, 'quantity': 10}
        ],
        'intraSystemNeighbors': [60003761, 60003762]  # Station IDs within Jita connected to this one
    },
    60003761: {  # Another station in Jita
        'solarSystemID': 30000142,  # Jita
        'buyOrders': [],
        'sellOrders': [],
        'intraSystemNeighbors': [60003760]  # Only connected to the Caldari Navy Assembly Plant
    }
}

# Initialize systemData and stationData as empty dicts
systemData = {}
stationData = {}
regionlist = '''10000001 Derelik
10000002 TheForge
10000003 ValeoftheSilent
10000004 UUA-F4
10000005 Detorid
10000006 WickedCreek
10000007 Cache
10000008 ScaldingPass
10000009 Insmother
10000010 Tribute
10000011 GreatWildlands
10000012 Curse
10000013 Malpais
10000014 Catch
10000015 Venal
10000016 Lonetrek
10000017 J7HZ-F
10000018 TheSpire
10000019 A821-A
10000020 Tash-Murkon
10000021 OuterPassage
10000022 Stain
10000023 PureBlind
10000025 Immensea
10000027 EtheriumReach
10000028 MoldenHeath
10000029 Geminate
10000030 Heimatar
10000031 Impass
10000032 SinqLaison
10000033 TheCitadel
10000034 TheKalevalaExpanse
10000035 Deklein
10000036 Devoid
10000037 Everyshore
10000038 TheBleakLands
10000039 Esoteria
10000040 Oasa
10000041 Syndicate
10000042 Metropolis
10000043 Domain
10000044 Solitude
10000045 Tenal
10000046 Fade
10000047 Providence
10000048 Placid
10000049 Khanid
10000050 Querious
10000051 CloudRing
10000052 Kador
10000053 CobaltEdge
10000054 Aridia
10000055 Branch
10000056 Feythabolis
10000057 OuterRing
10000058 Fountain
10000059 ParagonSoul
10000060 Delve
10000061 Tenerifis
10000062 Omist
10000063 Period Basis
10000064 Essence
10000065 Kor-Azor
10000066 PerrigenFalls
10000067 Genesis
10000068 VergeVendor
10000069 BlackRise'''.split('\n')
regionlis = {}
for reg in regionlist:
    temp = reg.split(' ')
    regionlis[temp[1]] = int(temp[0])

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
    """Traverse the directory structure to build systemData with high-security systems."""
    root_dir = os.path.join(os.getcwd(), 'eve')  # Relative path

    # Walk through all subdirectories and collect system data
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename == 'solarsystem.yaml':
                filepath = os.path.join(dirpath, filename)
                with open(filepath, 'r') as file:
                    try:
                        data = yaml.safe_load(file)
                    except yaml.YAMLError as exc:
                        print(f"Error parsing YAML file {filepath}: {exc}")
                        continue
                
                security = data['security']
                # Only include high-security systems
                if security >= highsec:
                    system_name = os.path.basename(dirpath)
                    parts = dirpath[len(root_dir) + 1:].split(os.sep)
                    region = parts[0]
                    consta = parts[1]
                    system = parts[2]
                    
                    regionID = regionlis[region]  # Get the correct region ID
                    solarSystemID = data['solarSystemID']
                    stargates = getStargates(data['stargates'])  # Extract stargates using updated function

                    # Add system data only if it's high-security
                    systemData[solarSystemID] = {
                        'security': data['security'],
                        'regionID': regionID,
                        'region': region,
                        'constellation': consta,
                        'stations': [],  # Stations will be filled later
                        'stargates': stargates,  # Now contains structured stargate data
                        'neighbors': []  # This will store neighboring systems
                    }
                    for syyss in systemData:
                        if systemData[syyss]['security'] > highsec:
                            for strrgt in systemData[syyss]['stargates']:
                                for strrgt1 in systemData[solarSystemID]['stargates']:
                                    if strrgt == systemData[solarSystemID]['stargates'][strrgt1]['destination']:
                                        # Check if neighbors key exists and append neighbors
                                        if 'neighbors' not in systemData[syyss]:
                                            systemData[syyss]['neighbors'] = []
                                        if 'neighbors' not in systemData[solarSystemID]:
                                            systemData[solarSystemID]['neighbors'] = []
                                        
                                        systemData[syyss]['neighbors'].append(solarSystemID)
                                        systemData[solarSystemID]['neighbors'].append(syyss)
                                        
                                        systemData[syyss]['stargates'][strrgt]['destinationSystem'] = solarSystemID
                                        systemData[solarSystemID]['stargates'][strrgt1]['destinationSystem'] = syyss
                    
                    print(parts, f'{(100*len(systemData)/1193):.2f}% done building universe')


    for syyss in list(systemData.keys()):
        if systemData[syyss]['neighbors'] == []:
            systemData.pop(syyss)
            continue
        for stargate in list(systemData[syyss]['stargates'].keys()):
            if 'destinationSystem' not in systemData[syyss]['stargates'][stargate].keys():
                systemData[syyss]['stargates'].pop(stargate)
                                    

def buildStationData(stations, market_data):
    """Map market data and stations into stationData and fill systemData."""
    for station in stations:
        station_id = station['stationID']
        solarSystemID = station['solarSystemID']

        # Only add the station if the system is in the high-security systemData
        if solarSystemID in systemData:
            # Initialize station entry in stationData
            stationData[station_id] = {}
            for stationAttribute in station.keys():
                if stationAttribute != 'stationID':
                    stationData[station_id][stationAttribute] = station[stationAttribute]
            stationData[station_id]['intraSystemNeighbors'] = []
            # Add the station to its system in systemData
            systemData[solarSystemID]['stations'].append(station_id)

def processIntraSystemNeighbors():
    """Process intra-system station connections."""
    count = 0
    total = len(systemData)
    # Assuming we have a method to determine which stations are neighbors
    for systemID, system in systemData.items():
        stations_in_system = system['stations']

        # Here you could add logic to determine intra-system neighbors
        for station_id in stations_in_system:
            stationData[station_id]['intraSystemNeighbors'] = [s for s in stations_in_system if s != station_id]

        for neighbor in system['neighbors']:
            if 'interSystemNeighbors' not in stationData[station_id].keys():
                stationData[station_id]['interSystemNeighbors'] = []
            for s in systemData[neighbor]['stations']:
                if s not in stationData[station_id]['interSystemNeighbors']:
                    stationData[station_id]['interSystemNeighbors'].append(s)
        count += 1
        print(f'processing Neighbors... {100*count//total}% done.') if count % 10 == 0 else None

# Load stations and market data
stations = yaml.safe_load(open('staStations.yaml', 'r'))
market_data = json.load(open('market_orders.json', 'r'))

# Walk through the universe and build the systemData structure
walkTheUniverse()

print('loaded')

# Map market data to stations and fill stationData
buildStationData(stations, market_data)

# Add intra-system neighbors
processIntraSystemNeighbors()

# Output data for debugging
open('systemData.json', 'w').write(json.dumps(systemData, indent=2))
open('stationData.json', 'w').write(json.dumps(stationData, indent=2))
