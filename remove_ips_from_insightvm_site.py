# filename: insightvm_remove_ips.py
import requests
import json
import os
import time
import logging
from requests.auth import HTTPBasicAuth

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Disable warnings for SSL verification for this session
requests.packages.urllib3.disable_warnings()

def remove_ips_from_insightvm_site(ips, site_id):
    session = requests.Session()
    session.verify = False
    username = os.getenv('INSIGHTVM_USERNAME')
    password = os.getenv('INSIGHTVM_PASSWORD')
    base_url = os.getenv('INSIGHTVM_BASE_URL')
    url = f"{base_url}/api/3/sites/{site_id}/included_targets"
    responses = []

    for ip in ips:
        try:
            response = session.delete(url, auth=HTTPBasicAuth(username, password), json=[ip], headers={'Content-Type': 'application/json'})
            if response.status_code == 429:
                time.sleep(60)
                response = session.delete(url, auth=HTTPBasicAuth(username, password), json=[ip], headers={'Content-Type': 'application/json'})
            if response.status_code in [200, 201]:
                responses.append({'ip': ip, 'status': 'success'})
            else:
                error_message = response.json().get('message', 'No error message provided')
                responses.append({'ip': ip, 'status': 'error', 'message': error_message, 'http_status': response.status_code, 'response_content': response.text})
        except requests.exceptions.RequestException as e:
            responses.append({'ip': ip, 'status': 'error', 'message': str(e)})

    return json.dumps(responses, indent=4)

# Example function call
if __name__ == "__main__":
    ips_to_remove = ["8.8.8.8", "4.4.4.4", "1.1.1.1"]
    site_id = 201
    result = remove_ips_from_insightvm_site(ips_to_remove, site_id)
    print(result)
