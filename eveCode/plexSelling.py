import requests

PLEX_TYPE_ID = 44992  # Type ID for PLEX in EVE Online
REGIONS_API = "https://evetycoon.com/api/v1/market/regions"  # Endpoint for region list
MARKET_STATS_API = "https://evetycoon.com/api/v1/market/stats/{region_id}/{type_id}"  # Market stats per region

def get_all_regions():
    """Fetches all region IDs from EveTycoon API."""
    response = requests.get(REGIONS_API)
    if response.status_code != 200:
        print("Failed to fetch region list.")
        return []
    
    regions = response.json()
    return [region["id"] for region in regions]  # Extracts only the IDs

def get_highest_min_sell_region():
    """Finds the region with the highest minimum sell price for PLEX."""
    regions = get_all_regions()
    if not regions:
        print('error')
        return None, None

    highest_min_sell = 0
    best_region = None

    for region_id in regions:
        url = MARKET_STATS_API.format(region_id=region_id, type_id=PLEX_TYPE_ID)
        response = requests.get(url)

        if response.status_code != 200:
            print(f"Failed to fetch market data for region {region_id}.")
            continue

        market_data = response.json()
        min_sell = market_data.get("sellMin", 0)  # Get the lowest sell order price

        if min_sell > highest_min_sell:
            highest_min_sell = min_sell
            best_region = region_id

    return best_region, highest_min_sell

best_region, highest_price = get_highest_min_sell_region()
if best_region:
    print(f"Best region to sell PLEX: {best_region} with a minimum sell price of {highest_price:.2f} ISK")
else:
    print("Could not determine the best region to sell PLEX.")
