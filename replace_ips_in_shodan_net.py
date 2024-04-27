# filename: replace_ips_in_shodan_net.py

import os
import requests
import json
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Environment variables
SHODAN_BASE_URL = os.getenv('SHODAN_BASE_URL')
SHODAN_API_KEY = os.getenv('SHODAN_API_KEY')

# Function to replace IPs in Shodan network
def replace_ips_in_shodan_net(ip_list, network_name):
    # creating Session object and declaring the verify variable to False
    session = requests.Session()
    session.verify = False

    # Retrieve the alert ID associated with the network name
    try:
        response = session.get(f"{SHODAN_BASE_URL}/shodan/alert/info?key={SHODAN_API_KEY}")
        response.raise_for_status()
        alerts = response.json()
        alert_id = None
        for alert in alerts:
            if alert.get('name') == network_name:
                alert_id = alert.get('id')
                break
        if not alert_id:
            logging.error(f"No alert found with the name: {network_name}")
            return None

        logging.debug(f"Retrieved alert ID for network: {network_name}")

    except requests.exceptions.RequestException as e:
        logging.error(f"Error retrieving alert ID: {e}")
        return None

    # Prepare the payload
    payload = {
        "filters": {
            "ip": ip_list,
        }
    }

    # Make the API call to replace IPs
    try:
        response = session.post(f"{SHODAN_BASE_URL}/shodan/alert/{alert_id}?key={SHODAN_API_KEY}",
                                headers={'Content-Type': 'application/json'},
                                data=json.dumps(payload))
        if response.status_code == 429:
            # Handle rate limiting with exponential backoff
            retry_after = int(response.headers.get('Retry-After', 60))
            logging.warning(f"Rate limit exceeded. Retrying after {retry_after} seconds.")
            time.sleep(retry_after)
            return replace_ips_in_shodan_net(ip_list, network_name)
        response.raise_for_status()
        logging.debug(f"IPs successfully replaced in the network: {network_name}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error replacing IPs in Shodan network: {e}")
        return None

# Example function call
if __name__ == "__main__":
    example_ips = ["8.8.8.8", "4.4.4.4"]
    network_name = "Cloud Public IPs (Cloudflare)"
    result = replace_ips_in_shodan_net(example_ips, network_name)
    print(result)