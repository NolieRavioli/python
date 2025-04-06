import os
import time
import asyncio
import itertools
import string
import json
import subprocess

USER_DEFINED_TLDS = ["com"] # User-defined TLDs to check.
ALPHANUM = string.ascii_lowercase # Allowed characters for domain generation.
RESULTS_FILE = "domain_results.txt"
DOMAIN_LENGTH = [4]  # e.g., check 3-letter domains.
BATCH_SIZE = 30
BATCH_INTERVAL = 1/5  # seconds per batch request
LOGGING = 2
# Load or generate the WHOIS database.
def load_whois_data():
    if not os.path.exists("whois.data"):
        debug_print(0, "whois.data not found. Generating it using generateWhoisDatabase.py")
        # This call assumes that generateWhoisDatabase.py is in the same folder and that it writes whois.data.
        subprocess.run(["python", "generateWhoisDatabase.py"], check=True)
    with open("whois.data", "r") as f:
        data = json.load(f)
    return data

# Load WHOIS data; use only the user-defined TLDs.
whois_data = load_whois_data()
# Use only keys from whois_data that are in USER_DEFINED_TLDS.
TLDs = [tld for tld in whois_data if tld in USER_DEFINED_TLDS]

def debug_print(level, message):
    """Prints a message if LOGGING is equal or greater than the specified level."""
    if LOGGING >= level:
        print(message)

def load_checkpoint():
    """If RESULTS_FILE exists, load its last line to use as a checkpoint.
       Returns the last processed domain (without the TLD) or None."""
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "r") as f:
            lines = f.readlines()
            if lines:
                last_line = lines[-1].strip()
                if last_line:
                    domain_checked = last_line.split()[0]
                    dot_index = domain_checked.find('.')
                    if dot_index != -1:
                        debug_print(3, domain_checked[:dot_index])
                        return domain_checked[:dot_index]
    return None

def generate_all_domains(lengthsList):
    """Generate all domains (e.g., 'aaa.net', 'aaa.com', etc.) for the allowed TLDs in lexicographical order."""
    domains = []
    for length in lengthsList:
        for combo in itertools.product(ALPHANUM, repeat=length):
            for tld in TLDs:
                domains.append(''.join(combo) + '.' + tld)
    domains.sort()
    return domains

count = 0
async def check_domain(full_domain):
    """
    Check a domain's availability by connecting to the WHOIS server
    specified for its TLD (as loaded from whois.data).
    Returns a tuple: (domain, result) where result is "available",
    "not available", or an error message.
    """
    try:
        # Extract TLD from the domain.
        tld = full_domain.split('.')[-1]
        whois_server = whois_data.get(tld)
        if not whois_server:
            return (full_domain, f"error: no whois server found for TLD {tld}")
        reader, writer = await asyncio.open_connection(whois_server, 43)
        query = full_domain + "\r\n"
        writer.write(query.encode())
        await writer.drain()
        response = await reader.read(-1)
        writer.close()
        await writer.wait_closed()
        response = response.decode('utf-8', errors='replace')
        # debug_print(3, response)
        debug_print(3, f'processing {full_domain}')
        # For many domains, a response containing "No match for" indicates the domain is available.
        if "No match for" in response:
            debug_print(1, f"{full_domain} available")
            return (full_domain, "available")
        else:
            global count
            count += 1
            debug_print(2, f"{full_domain} not available ({count} domains processed)") if count%100 == 0 else debug_print(3, f"{full_domain} available")
            return (full_domain, "not available")
    except Exception as e:
        print(e)
        return (full_domain, f"error: {e}")

async def main():
    checkpoint = load_checkpoint()
    if checkpoint:
        debug_print(1, f"Resuming after checkpoint: {checkpoint}")
    else:
        debug_print(1, "No checkpoint found, starting from the beginning.")

    all_domains = generate_all_domains(DOMAIN_LENGTH)
    # If a checkpoint exists, skip all domains up to and including that domain.
    if checkpoint:
        try:
            idx = all_domains.index(checkpoint)
            all_domains = all_domains[idx+1:]
        except ValueError:
            pass

    total_domains = len(all_domains)
    debug_print(2, f"Total domains to check in this run: {total_domains}")

    # Process domains in batches with a concurrency limit equal to BATCH_SIZE.
    for i in range(0, total_domains, BATCH_SIZE):
        t1 = time.time()
        batch = all_domains[i:i+BATCH_SIZE]
        tasks = [check_domain(domain) for domain in batch]
        results = await asyncio.gather(*tasks)
        # Append each result to the file.
        for full_domain, result in results:
            if result == "available":
                with open(RESULTS_FILE, "a") as f:
                    f.write(f"{full_domain}\n")
            else:
                pass  # Optionally log "not available" or errors.
        # Calculate execution time and sleep for the remainder of the BATCH_INTERVAL.
        elapsed = time.time() - t1
        sleep_time = BATCH_INTERVAL - elapsed
        if sleep_time > 0:
            await asyncio.sleep(sleep_time)

if __name__ == "__main__":
    asyncio.run(main())
