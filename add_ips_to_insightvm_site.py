# filename: add_ips_to_insightvm_site.py
import os
import requests
import json
import logging
from requests.auth import HTTPBasicAuth
from urllib3.exceptions import InsecureRequestWarning

# Set up logging
logging.basicConfig(level=logging.INFO)

# Suppress only the single InsecureRequestWarning from urllib3 needed
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def add_ips_to_insightvm_site(ips, site_id):
    # Environment variables
    username = os.getenv('INSIGHTVM_USERNAME')
    password = os.getenv('INSIGHTVM_PASSWORD')
    base_url = os.getenv('INSIGHTVM_BASE_URL')

    # Endpoint for adding IPs to a site
    endpoint = f"{base_url}/api/3/sites/{site_id}/included_targets"

    # Create a session object
    session = requests.Session()
    session.verify = False  # Disable SSL verification
    session.auth = HTTPBasicAuth(username, password)

    # Initialize response list
    responses = []

    # Add each IP to the site
    for ip in ips:
        try:
            response = session.post(endpoint, json=[ip])
            if response.status_code == 201:
                responses.append({'ip': ip, 'status': 'success'})
                logging.debug(f"Successfully added IP {ip} to site {site_id}.")
            else:
                error_message = response.json()
                responses.append({'ip': ip, 'status': 'error', 'message': error_message})
                logging.debug(f"Failed to add IP {ip} to site {site_id}: {error_message}")
        except requests.exceptions.RequestException as e:
            responses.append({'ip': ip, 'status': 'error', 'message': str(e)})
            logging.error(f"An error occurred while adding IP {ip} to site {site_id}: {e}")

    # Return the response list as JSON
    return json.dumps(responses, indent=2)

# Example function call
if __name__ == "__main__":
    example_ips = ["8.8.8.8", "4.4.4.4"]
    example_site_id = 201
    result = add_ips_to_insightvm_site(example_ips, example_site_id)
    print(result)