import requests

# Define the regions
regions = [
    "10000001", "10000002", "10000003", "10000005", "10000006", "10000007", "10000008", "10000009",
    "10000010", "10000011", "10000012", "10000014", "10000015", "10000016", "10000020", "10000022",
    "10000025", "10000027", "10000028", "10000029", "10000030", "10000031", "10000032", "10000033",
    "10000034", "10000035", "10000036", "10000037", "10000038", "10000041", "10000042", "10000043",
    "10000044", "10000045", "10000046", "10000047", "10000048", "10000049", "10000050", "10000051",
    "10000052", "10000054", "10000058", "10000059", "10000060", "10000064", "10000065", "10000066",
    "10000067", "10000068", "10000069"
]

# PLEX type ID
PLEX_TYPE_ID = 44992

# ESI URL for market orders
ESI_BASE_URL = "https://esi.evetech.net/latest/markets/{}/orders/"

def check_plex_orders_in_region(region_id):
    try:
        response = requests.get(ESI_BASE_URL.format(region_id), params={"type_id": PLEX_TYPE_ID})
        if response.status_code == 200:
            data = response.json()
            if data:
                return True  # PLEX orders found in this region
        return False
    except requests.RequestException as e:
        print(f"Failed to retrieve data for region {region_id}: {e}")
        return False

def main():
    regions_with_plex = []
    
    for region in regions:
        if check_plex_orders_in_region(region):
            regions_with_plex.append(region)
            print(f"PLEX orders found in region {region}")
    
    print("\nRegions with PLEX on the market:")
    for region in regions_with_plex:
        print(region)

if __name__ == "__main__":
    main()
