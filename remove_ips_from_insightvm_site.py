# filename: insightvm_remove_ips.py
import requests
import json
import os
import time
import logging
from requests.auth import HTTPBasicAuth

# Configure logging
logging.basicConfig(level=logging.INFO)

# Disable warnings for SSL verification for this session
requests.packages.urllib3.disable_warnings()

def remove_ips_from_insightvm_site(ips, site_id):
    # Set up the session
    session = requests.Session()
    session.verify = False

    # Retrieve environment variables
    username = os.getenv('INSIGHTVM_USERNAME')
    password = os.getenv('INSIGHTVM_PASSWORD')
    base_url = os.getenv('INSIGHTVM_BASE_URL')

    # Endpoint for removing IPs from a site
    url = f"{base_url}/api/3/sites/{site_id}/included_targets"

    # Prepare the response dictionary
    response_dict = {}

    # Loop through the IPs and attempt to remove each one
    for ip in ips:
        try:
            # Make the DELETE request
            response = session.delete(url, auth=HTTPBasicAuth(username, password), json=[ip], headers={'Content-Type': 'application/json'})

            # Check for rate limiting and implement backoff
            if response.status_code == 429:
                logging.warning(f"Rate limit exceeded while trying to remove IP {ip}. Retrying after 60 seconds...")
                time.sleep(60)  # Simple backoff strategy: wait for 60 seconds
                response = session.delete(url, auth=HTTPBasicAuth(username, password), json=[ip], headers={'Content-Type': 'application/json'})

            # Process the response
            if response.status_code in [200, 201]:
                logging.debug(f"Successfully removed IP {ip} from site {site_id}.")
                response_dict[ip] = {'status': 'success'}
            else:
                # Log detailed error information
                error_message = response.json().get('message', 'No error message provided')
                response_dict[ip] = {'status': 'error', 'message': error_message, 'http_status': response.status_code, 'response_content': response.text}
                logging.error(f"Failed to remove IP {ip}: {error_message}")

        except requests.exceptions.RequestException as e:
            # Log the exception
            logging.error(f"An exception occurred while trying to remove IP {ip}: {str(e)}")
            response_dict[ip] = {'status': 'error', 'message': str(e)}

    # Return the response dictionary
    return json.dumps(response_dict, indent=4)

# Example function call
if __name__ == "__main__":
    ips_to_remove = ["8.8.8.8", "4.4.4.4", "1.1.1.1"]
    site_id = 201
    result = remove_ips_from_insightvm_site(ips_to_remove, site_id)
    print(result)
