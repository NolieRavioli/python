import os
import yaml

# [system_name,solarSystemID,region,stargates]

active_regions = [10000054, 10000069, 10000001, 10000036, 10000043, 10000064, 10000037, 10000067, 10000030, 10000052, 10000049, 10000065, 10000016, 10000042, 10000028, 10000048, 10000032, 10000044, 10000020, 10000038, 10000033, 10000002, 10000068]

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

stations = yaml.safe_load(open(r'C:\Users\Nolan\Desktop\Eve Online Code\staStations.yaml', 'r'))

active = []

def getStargates(a):
    out = []
    for b in a:
        out.append((b,a[b]['destination']))
    return out

def main():
    root_dir = r'C:\Users\Nolan\Desktop\Eve Online Code\eve'
    output_file = 'output.txt'
    highsec_threshold = 0.5  # Threshold for high-security systems

    highsec_systems = []

    # Walk through all subdirectories and files
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename == 'solarsystem.yaml':
                filepath = os.path.join(dirpath, filename)
                with open(filepath, 'r') as file:
                    try:
                        data = yaml.safe_load(file)
                        # Get the security value; default to 0 if not found
                        security = data['security']
                        
                        if security >= highsec_threshold:
                            # Assume the system name is the folder name containing the yaml file
                            system_name = os.path.basename(dirpath)
                            activestations = []
                            parts = dirpath[43:].split('\\')
                            region = parts[0]
                            consta = parts[1]
                            system = parts[2]
                            regionID = regionlis[region]
                            solarSystemID = data['solarSystemID']
                            stargates = getStargates(data['stargates'])
                            for station in stations:
                                if station['solarSystemID'] == solarSystemID:
                                    activestations.append([station['stationName'],station['stationID'],station['dockingCostPerVolume'],station['maxShipVolumeDockable']])
                            temppr = [(system_name,solarSystemID),(region,regionID),stargates,activestations]
                            print(100*len(highsec_systems)/1074)
                            if (region,regionID) not in active:
                                active.append((region,regionID))
                                print(region)
                            highsec_systems.append(temppr)
                    except yaml.YAMLError as exc:
                        print(f"Error parsing YAML file {filepath}: {exc}")



    # Write the list of high-security systems to output.txt
    with open(output_file, 'w') as outfile:
        for sys in highsec_systems:
            outfile.write(str(sys) + '\n')

    print(f"High-security systems have been listed in {output_file}."+str(len(highsec_systems)))
    print(active)

if __name__ == '__main__':
    main()
