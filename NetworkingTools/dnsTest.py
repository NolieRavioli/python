import time
import socket
import subprocess

dns_servers = [
    {"name": "Comcast Primary", "ip": "75.75.75.75"},
    {"name": "Comcast Secondary", "ip": "75.75.76.76"},
    {"name": "Google Primary", "ip": "8.8.8.8"},
    {"name": "Google Secondary", "ip": "8.8.4.4"},
    {"name": "Cloudflare Primary", "ip": "1.1.1.1"},
    {"name": "Cloudflare Secondary", "ip": "1.0.0.1"},
    {"name": "OpenDNS Primary", "ip": "208.67.222.222"},
    {"name": "OpenDNS Secondary", "ip": "208.67.220.220"},
    {"name": "Comcast Denver", "ip": "216.148.227.68"},
    {"name": "Comcast Denver Backup", "ip": "204.127.202.4"},
]

def ping_latency(server_ip):
    try:
        result = subprocess.run(["ping", "-n", "3", server_ip], capture_output=True, text=True)
        lines = result.stdout.split("\n")
        for line in lines:
            if "Average" in line:
                avg_latency = line.split("=")[-1].strip().replace("ms", "")
                return float(avg_latency)
    except Exception as e:
        return None

def dns_resolution_time(server_ip):
    try:
        start = time.time()
        result = subprocess.run(["nslookup", "ffqq.gg", server_ip], capture_output=True, text=True)
        end = time.time()
        return (end - start) * 1000  # Convert to ms
    except Exception as e:
        return None

def main():
    print("DNS Latency and Resolution Test (Cache Bypassed)\n")
    print("{:<25} {:<15} {:<15}".format("DNS Server", "Ping Latency (ms)", "DNS Query Time (ms)"))
    print("-" * 60)
    
    for server in dns_servers:
        ping_time = ping_latency(server["ip"])
        dns_time = dns_resolution_time(server["ip"])
        print("{:<25} {:<15} {:<15}".format(server["name"], f"{ping_time:.2f}" if ping_time else "N/A", f"{dns_time:.2f}" if dns_time else "N/A"))

if __name__ == "__main__":
    main()
