import requests
import json
import time

global total_requests

# List of region IDs with high sec systems
active_regions = [10000054, 10000069, 10000001, 10000036, 10000043, 10000064, 
                  10000037, 10000067, 10000030, 10000052, 10000049, 10000065, 
                  10000016, 10000042, 10000028, 10000048, 10000032, 10000044, 
                  10000020, 10000038, 10000033, 10000002, 10000068]

# ESI API base URL
base_url = "https://esi.evetech.net/latest/markets/{}/orders/"

# Specify order_type as 'all' to get both buy and sell orders
order_type = 'all'


def saveProg(all_market_orders):
    # Save the results to a file
    with open('market_orders.json', 'w') as f:
        json.dump(all_market_orders, f, indent=2)
    print("Progress saved: all market orders fetched so far.")


# Get the total number of requests needed by fetching the first page of each region
def get_total_requests():
    total_requests = 0
    pages_per_region = {}

    for region_id in active_regions:
        try:
            response = requests.get(base_url.format(region_id), params={
                'order_type': order_type,
                'page': 1
            })

            if response.status_code != 200:
                print(f"Error fetching data for region {region_id}: "
                      f"Received status code {response.status_code}")
                exit(1)

            # Get total pages from the response headers
            total_pages = int(response.headers.get('x-pages', 1))
            pages_per_region[region_id] = total_pages
            total_requests += total_pages
            print(f"Region {region_id} has {total_pages} pages.")
        except Exception as e:
            print(f"Error while fetching page 1 for region {region_id}: {e}")
            exit(1)

    return pages_per_region, total_requests


# Define a function to fetch all pages of market orders for a given region
def fetch_region_orders(region_id, total_pages, order_type='all', max_retries=5, retry_delay=2):
    region_orders = []
    page = 1
    count = 0

    while page <= total_pages:
        try:
            response = requests.get(base_url.format(region_id), params={
                'order_type': order_type,
                'page': page
            })

            if response.status_code != 200:
                count += 1
                print(f"Error fetching data for region {region_id} on page {page}: "
                      f"Received status code {response.status_code}. Retry count: {count}")
                if count > max_retries:
                    print(f"Max retries reached for region {region_id}. Saving progress and exiting.")
                    saveProg(all_orders)
                    exit(1)
                time.sleep(retry_delay)  # Delay before retrying
                continue  # Retry the same page

            # Reset retry count on successful response
            count = 0

            # Extract orders from response
            orders = response.json()
            region_orders.extend(orders)
            comple = page+completed_requests
            eta = ((time.time()-t1)/(comple))*(total_requests-comple)
            etaStack = [int(eta//3600),int(eta//60)%60,int(eta)%60]
            print(f"Fetched page {page}/{total_pages} for region {region_id}. ({((comple/total_requests)*100):.2f}% done) ETA: {etaStack[0]} hr {etaStack[1]}:{etaStack[2]}")
            page += 1

        except requests.exceptions.RequestException as e:
            print(f"RequestException for region {region_id} on page {page}: {e}")
            count += 1
            if count > max_retries:
                print(f"Max retries reached due to exceptions. Saving progress and exiting.")
                saveProg(all_orders)
                exit(1)
            time.sleep(retry_delay)  # Delay before retrying

    return region_orders


# Loop over each region and fetch orders while updating the progress
def fetch_all_regions_orders(pages_per_region, total_requests):
    global completed_requests
    all_orders = {}
    completed_requests = 0

    for region_id, total_pages in pages_per_region.items():
        print(f"Fetching market orders for region {region_id}")
        region_orders = fetch_region_orders(region_id, total_pages, order_type)

        all_orders[region_id] = region_orders

        completed_requests += total_pages

    return all_orders


# Main function to start the process
if __name__ == "__main__":
    try:
        # Step 1: Get total number of requests across all regions
        pages_per_region, total_requests = get_total_requests()

        # Step 2: Fetch all orders and track progress
        t1 = time.time()
        all_orders = fetch_all_regions_orders(pages_per_region, total_requests)

        # Step 3: Save all results
        saveProg(all_orders)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        saveProg(all_orders)  # Save progress in case of a critical error
        exit(1)
