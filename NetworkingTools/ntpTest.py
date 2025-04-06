import ntplib
import socket

# List of NTP servers to test.
servers = [
    {"name": "time-a-b.nist.gov", "address": "132.163.96.1"},
    {"name": "time-b-b.nist.gov", "address": "132.163.96.2"},
    {"name": "time-c-b.nist.gov", "address": "132.163.96.3"},
    {"name": "time-d-b.nist.gov", "address": "132.163.96.4"},
    # IPv6 servers: ntplib may not support IPv6 out-of-the-box.
    {"name": "time-d-b.nist.gov (IPv6)", "address": "2610:20:6f96:96::4"},
    {"name": "time-e-b.nist.gov", "address": "132.163.96.6"},
    {"name": "time-e-b.nist.gov (IPv6)", "address": "2610:20:6f96:96::6"},
    {"name": "time.nist.gov", "address": "time.nist.gov"},
    {"name": "utcnist.colorado.edu", "address": "128.138.140.44"},
    {"name": "utcnist2.colorado.edu", "address": "128.138.141.172"},
    {"name": "utcnist3.colorado.edu", "address": "128.138.140.211"},
    {"name": "0.pool.ntp.org", "address": "0.pool.ntp.org"}
]

def query_ntp(server_address):
    client = ntplib.NTPClient()
    try:
        # The request sends an NTP packet and returns a response with several timing metrics.
        response = client.request(server_address, version=3, timeout=5)
        # response.delay is the round-trip delay in seconds.
        # response.offset is the time difference between server and client.
        return response.delay, response.offset
    except Exception as e:
        return None, f"Error: {e}"

def main():
    print("NTP Latency and Offset Testing:")
    for server in servers:
        address = server["address"]
        # ntplib by default uses IPv4, so skip IPv6 addresses
        if ":" in address:
            print(f"{server['name']} ({address}): Skipped (IPv6 not supported by ntplib)")
            continue
        delay, result = query_ntp(address)
        if delay is None:
            print(f"{server['name']} ({address}): {result}")
        else:
            print(f"{server['name']} ({address}): Delay = {delay * 1000:.2f} ms, Offset = {result * 1000:.2f} ms")

if __name__ == "__main__":
    main()
