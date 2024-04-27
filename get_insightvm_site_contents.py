# filename: get_insightvm_site_contents.py
import os
import requests
import json
import logging
import time
from ipaddress import ip_network, ip_address

# Environment variables
INSIGHTVM_USERNAME = os.getenv('INSIGHTVM_USERNAME')
INSIGHTVM_PASSWORD = os.getenv('INSIGHTVM_PASSWORD')
INSIGHTVM_BASE_URL = os.getenv('INSIGHTVM_BASE_URL')

# Configure logging
logging.basicConfig(level=logging.INFO)

def expand_subnet(ip):
    try:
        if '/' not in ip and '-' not in ip:
            # It's a single IP, not a subnet or range
            logging.debug(f"Processing single IP address: {ip}")
            return [ip]
        network = ip_network(ip, strict=False)
        subnet_ips = [str(ip) for ip in network.hosts()] if network.prefixlen != 32 else [str(network.network_address)]
        logging.debug(f"Expanded subnet {ip} to {len(subnet_ips)} IP addresses")
        return subnet_ips
    except ValueError:
        logging.error(f"Invalid IP address or subnet: {ip}")
        return []

def expand_ip_range(ip_range):
    start_ip, end_ip = ip_range.split('-')
    start_ip = ip_address(start_ip.strip())
    end_ip = ip_address(end_ip.strip())
    range_ips = [str(ip) for ip in range(int(start_ip), int(end_ip) + 1)]
    logging.debug(f"Expanded IP range from {start_ip} to {end_ip} into {len(range_ips)} IP addresses")
    return range_ips

def get_insightvm_site_contents(site_id):
    # Disable SSL warnings
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

    # Create a session object
    session = requests.Session()
    session.verify = False

    # Set up basic authentication
    session.auth = (INSIGHTVM_USERNAME, INSIGHTVM_PASSWORD)

    # Initialize list to store IP addresses
    ip_addresses = []

    # Define the base URL for the API call
    url = f"{INSIGHTVM_BASE_URL}/api/3/sites/{site_id}/included_targets"

    try:
        response = session.get(url)
        if response.status_code == 200:
            logging.debug(f"Successfully retrieved data for site ID {site_id}")
            data = response.json()
            addresses = data.get('addresses')
            if not addresses:
                logging.debug("No addresses found in the response.")
            for ip in addresses:
                if '-' in ip:
                    # IP range detected, expand it
                    ip_addresses.extend(expand_ip_range(ip))
                else:
                    # Expand subnet if necessary and extend the list of IP addresses
                    ip_addresses.extend(expand_subnet(ip))
            logging.debug(f"Total IP addresses processed: {len(ip_addresses)}")
        elif response.status_code == 429:
            # Handle rate limiting
            logging.warning("Rate limit reached, sleeping for 60 seconds...")
            time.sleep(60)
        else:
            response.raise_for_status()

    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred: {e}")
        return None

    # Convert any integer IP addresses to dotted decimal notation
    ip_addresses = [str(ip_address(int(ip))) if ip.isdigit() else ip for ip in ip_addresses]

    # Output the list of IP addresses as JSON
    ip_addresses_json = json.dumps(ip_addresses, indent=4)
    return ip_addresses_json

# Example function call
if __name__ == "__main__":
    site_id = 201
    ip_list_json = get_insightvm_site_contents(site_id)
    if ip_list_json:
        print(ip_list_json)
