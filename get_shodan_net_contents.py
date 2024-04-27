# filename: get_shodan_net_contents.py
import os
import requests
import logging
import time
import json
from ipaddress import ip_network, ip_address

# Environment variables
SHODAN_BASE_URL = os.getenv('SHODAN_BASE_URL')
SHODAN_API_KEY = os.getenv('SHODAN_API_KEY')

# Configure logging
logging.basicConfig(level=logging.INFO)

def expand_ip_range(ip_range):
    start_ip, end_ip = ip_range.split('-')
    start_ip = ip_address(start_ip.strip())
    end_ip = ip_address(end_ip.strip())
    range_ips = [str(ip) for ip in range(int(start_ip), int(end_ip) + 1)]
    logging.debug(f"Expanded IP range {start_ip} to {end_ip} into {len(range_ips)} IP addresses")
    return range_ips

def get_shodan_net_contents(net_name):
    session = requests.Session()
    session.verify = False  # Avoid SSL validation issues

    # Define the API endpoint
    api_endpoint = f"{SHODAN_BASE_URL}/shodan/alert/info?key={SHODAN_API_KEY}"

    try:
        # Initial backoff time
        backoff_time = 1

        while True:
            response = session.get(api_endpoint)
            if response.status_code == 200:
                logging.debug("Successfully retrieved data from Shodan API.")
                break
            elif response.status_code == 429:
                logging.warning("Rate limit exceeded. Retrying after backoff.")
                time.sleep(backoff_time)
                backoff_time *= 2  # Exponential backoff
                continue
            else:
                response.raise_for_status()

        # Parse the response to JSON
        data = response.json()

        # Find the specified network
        for network in data:
            if network['name'] == net_name:
                logging.debug(f"Found network: {net_name}")
                # Extract the IP addresses and convert to /32 if necessary
                ip_list = []
                for ip in network['filters']['ip']:
                    if '-' in ip:
                        # IP range detected, expand it
                        ip_list.extend(expand_ip_range(ip))
                    else:
                        # Single IP or subnet
                        subnet = ip_network(ip, strict=False)
                        subnet_ips = [str(single_ip) for single_ip in subnet]
                        logging.debug(f"Processed subnet {ip} into {len(subnet_ips)} IP addresses")
                        ip_list.extend(subnet_ips)
                return json.dumps({"ip": ip_list}, indent=4)

        logging.error(f"Network name '{net_name}' not found.")
        return json.dumps({"error": "Network name not found."})

    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred: {e}")
        return json.dumps({"error": "An error occurred while making the API call."})

# Example function call
if __name__ == "__main__":
    net_contents = get_shodan_net_contents("Cloud Public IPs (Azure&AWS)")
    print(net_contents)
