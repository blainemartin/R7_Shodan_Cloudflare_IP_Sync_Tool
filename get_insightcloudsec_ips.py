import os
import requests
import json
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO)

# Retrieve environment variables
INSIGHTCLOUDSEC_BASE_URL = os.getenv('INSIGHTCLOUDSEC_BASE_URL')
INSIGHTCLOUDSEC_API_KEY = os.getenv('INSIGHTCLOUDSEC_API_KEY')

def get_insightcloudsec_ips():
    url = f"{INSIGHTCLOUDSEC_BASE_URL}/v3/public/resource/query"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Api-Key': INSIGHTCLOUDSEC_API_KEY
    }
    payload = {
        "selected_resource_type": "publicip",
        "limit": 1000,
        "offset": 0
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 429:
            logging.warning("Rate limit reached, retrying after some time...")
            time.sleep(60)  # Simple backoff strategy, wait for 60 seconds
            return get_insightcloudsec_ips()  # Retry the request

        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
        logging.debug("API call successful, processing data...")

        data = response.json()
        resources = data.get('resources', [])

        # Filter and reformat the data
        formatted_data = []
        for resource in resources:
            public_ip_info = resource.get('publicip', {}).get('common', {})
            if public_ip_info:
                formatted_entry = {
                    'IP Address': public_ip_info.get('resource_name'),
                    'Metadata': public_ip_info
                }
                formatted_data.append(formatted_entry)

        if formatted_data:
            logging.debug(f"Retrieved and formatted {len(formatted_data)} IP addresses.")
        else:
            logging.debug("No IP addresses found.")

        return json.dumps(formatted_data, indent=4)

    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        logging.error(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        logging.error(f"Timeout error occurred: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        logging.error(f"An error occurred: {req_err}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

# Call the function and print the result
if __name__ == "__main__":
    public_ips_json = get_insightcloudsec_ips()
    if public_ips_json:
        print(public_ips_json)