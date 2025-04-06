import os
import requests
from bs4 import BeautifulSoup
import time
import json

# Set logging level: 3 = DEBUG, 2 = INFO, 1 = BASIC, 0 = NONE
LOGGING = 1

def debug_print(level, message):
    """Prints a message if LOGGING is equal or greater than the specified level."""
    if LOGGING >= level:
        print(message)

# File to store WHOIS data (keys: TLDs, values: WHOIS server strings)
WHOIS_DATA_FILE = "whois.data"

# URL to retrieve the list of TLDs from IANA.
TLD_LIST_URL = "https://data.iana.org/TLD/tlds-alpha-by-domain.txt"
# Base URL for IANA TLD detail pages (format string expects the TLD in lowercase).
IANA_TLD_BASE_URL = "https://www.iana.org/domains/root/db/{}.html"

def load_or_generate_whois_dict():
    """
    Loads the WHOIS data from WHOIS_DATA_FILE if it exists.
    Otherwise, downloads the TLD list from IANA, creates a dictionary with keys
    for each TLD and empty values, saves it to WHOIS_DATA_FILE, and returns it.
    """
    if os.path.exists(WHOIS_DATA_FILE):
        debug_print(2, f"Loading WHOIS data from {WHOIS_DATA_FILE}")
        with open(WHOIS_DATA_FILE, "r") as f:
            try:
                whois_dict = json.load(f)
            except Exception as e:
                debug_print(1, f"Error loading JSON from {WHOIS_DATA_FILE}: {e}")
                whois_dict = {}
    else:
        debug_print(2, f"{WHOIS_DATA_FILE} not found. Generating new dictionary from IANA TLD list.")
        response = requests.get(TLD_LIST_URL)
        response.raise_for_status()
        lines = response.text.splitlines()
        # Exclude comment lines (first line is usually a comment)
        tlds = [line.strip().lower() for line in lines if not line.startswith("#")]
        whois_dict = {tld: "" for tld in tlds}
        with open(WHOIS_DATA_FILE, "w") as f:
            json.dump(whois_dict, f, indent=4)
        debug_print(2, f"Generated WHOIS data for {len(whois_dict)} TLDs and saved to {WHOIS_DATA_FILE}")
    return whois_dict

def get_whois_server_for_tld(tld):
    """
    Given a TLD, downloads its IANA page and attempts to extract the WHOIS server.
    Uses a parsing strategy based on finding the <b> tag containing "WHOIS Server:".
    Returns the WHOIS server string if found, or None otherwise.
    """
    url = IANA_TLD_BASE_URL.format(tld)
    debug_print(3, f"Requesting URL: {url}")
    response = requests.get(url)
    if response.status_code != 200:
        debug_print(1, f"Could not retrieve page for TLD {tld}, status code {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    if LOGGING >= 3:
        snippet = soup.get_text()[:200].strip().replace("\n", " ")
        debug_print(3, f"Page snippet for {tld}: {snippet}")

    # Look for a <b> tag that contains "WHOIS Server:".
    b_tag = soup.find("b", string=lambda text: text and "WHOIS Server:" in text)
    if b_tag:
        # Iterate over siblings until a non-empty text node is found.
        next_node = b_tag.next_sibling
        while next_node and (not hasattr(next_node, 'strip') or next_node.strip() == ""):
            next_node = next_node.next_sibling
        if next_node:
            server = next_node.strip()
            debug_print(3, f"Extracted WHOIS server for {tld}: {server}")
            return server
        else:
            debug_print(3, f"WHOIS Server tag found for {tld} but no following text node.")
            return None
    else:
        debug_print(3, f"No <b> tag with 'WHOIS Server:' found for {tld}.")
        return None

def write_whois_data(whois_dict):
    """
    Writes the current WHOIS dictionary to WHOIS_DATA_FILE in JSON format.
    """
    try:
        with open(WHOIS_DATA_FILE, "w") as f:
            json.dump(whois_dict, f, indent=4)
        debug_print(3, f"WHOIS data written to {WHOIS_DATA_FILE}")
    except Exception as e:
        debug_print(1, f"Error writing WHOIS data to file: {e}")

def process_whois_data():
    """
    Loads or generates the WHOIS dictionary, then iterates over each TLD key.
    For each TLD with an empty value, fetches its WHOIS server and updates the dictionary.
    The WHOIS dictionary is saved to file after processing each TLD.
    """
    whois_dict = load_or_generate_whois_dict()
    total = len(whois_dict)
    debug_print(1, f"Processing {total} TLDs...")
    
    for idx, tld in enumerate(list(whois_dict.keys()), start=1):
        # Only process TLDs with an empty value.
        if whois_dict[tld]:
            debug_print(3, f"Skipping {tld} as WHOIS server is already set: {whois_dict[tld]}")
            continue
        
        t1 = time.time()
        try:
            server = get_whois_server_for_tld(tld)
            if server:
                whois_dict[tld] = server
                debug_print(2, f"[{idx}/{total}] {tld}: {server}")
            else:
                debug_print(2, f"[{idx}/{total}] {tld}: No WHOIS server found")
        except Exception as e:
            debug_print(1, f"Error processing TLD {tld}: {e}")
        
        # Write current WHOIS data to file.
        write_whois_data(whois_dict)
        
        # Calculate execution time and sleep for the remainder of a 0.2-second interval.
        elapsed = time.time() - t1
        sleep_time = 0.2 - elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)
    return whois_dict

if __name__ == "__main__":
    whois_dict = process_whois_data()
    # Output the final WHOIS dictionary as formatted JSON.
    print("\nFinal WHOIS dictionary:")
    print(json.dumps(whois_dict, indent=4))
