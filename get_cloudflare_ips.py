import os  
import requests  
import time  
import logging  
from requests.exceptions import HTTPError, ConnectionError  
  
# Set up logging  
logging.basicConfig(level=logging.INFO)  
  
# Environment variables  
CLOUDFLARE_API_KEY = os.getenv('CLOUDFLARE_API_KEY')  
CLOUDFLARE_BASE_URL = os.getenv('CLOUDFLARE_BASE_URL')  
  
if not CLOUDFLARE_API_KEY or not CLOUDFLARE_BASE_URL:  
    raise EnvironmentError("Required environment variables CLOUDFLARE_API_KEY or CLOUDFLARE_BASE_URL are not set.")  
  
# Headers for Cloudflare API  
headers = {  
    'Authorization': f'Bearer {CLOUDFLARE_API_KEY}',  
    'Content-Type': 'application/json'  
}  
  
# Create a session object for persistent HTTP connections  
session = requests.Session()  
  
def backoff_handler(attempt, max_attempts=5):  
    """Calculate exponential backoff time and limit the number of attempts."""  
    if attempt >= max_attempts:  
        raise Exception("Maximum number of retry attempts reached.")  
    return min(2 ** attempt, 60)  # Cap the backoff at 60 seconds  
  
def call_cloudflare_api(url):  
    """Make a call to the Cloudflare API with error handling and backoff strategy."""  
    attempt = 0  
    while True:  
        try:  
            response = session.get(url, headers=headers)  
            response.raise_for_status()  
            logging.debug(f"Successfully made API call to {url}. Processing data...")  
            return response.json()  
        except HTTPError as http_err:  
            logging.error(f'HTTP error occurred: {http_err} - Status Code: {response.status_code}')  
            if response.status_code == 429:  # Rate limit exceeded  
                sleep_time = backoff_handler(attempt)  
                logging.debug(f'Rate limit exceeded. Retrying in {sleep_time} seconds.')  
                time.sleep(sleep_time)  
                attempt += 1  
            else:  
                raise  
        except ConnectionError as conn_err:  
            logging.error(f'Connection error occurred: {conn_err}')  
            sleep_time = backoff_handler(attempt)  
            logging.debug(f'Retrying in {sleep_time} seconds.')  
            time.sleep(sleep_time)  
            attempt += 1  
        except Exception as err:  
            logging.error(f'An error occurred: {err}')  
            raise  
  
def get_cloudflare_ips():  
    """Search for public IP addresses associated with DNS and load balancers."""  
    zones_url = f'{CLOUDFLARE_BASE_URL}/zones?per_page=50'  # Adjust per_page as needed  
    public_ips = []  
  
    # Fetch all zones with pagination  
    while zones_url:  
        zones_data = call_cloudflare_api(zones_url)  
        for zone in zones_data.get('result', []):  
            zone_id = zone['id']  
            logging.debug(f"Retrieved zone information for zone ID {zone_id}. Fetching DNS records...")  
            dns_records_url = f'{CLOUDFLARE_BASE_URL}/zones/{zone_id}/dns_records?per_page=100'  # Adjust per_page as needed  
              
            # Fetch all DNS records with pagination  
            while dns_records_url:  
                dns_records_data = call_cloudflare_api(dns_records_url)  
                for dns_record in dns_records_data.get('result', []):  
                    if dns_record['type'] in ('A', 'AAAA'):  # Check for IPv4 and IPv6 addresses  
                        public_ips.append({  
                            'type': dns_record['type'],  
                            'name': dns_record['name'],  
                            'content': dns_record['content'],  
                            'zone_id': zone_id  
                        })  
                        logging.debug(f"Retrieved {dns_record['type']} record for {dns_record['name']} with content {dns_record['content']}.")
                dns_records_url = dns_records_data.get('result_info', {}).get('next_page', None)  
  
        zones_url = zones_data.get('result_info', {}).get('next_page', None)  
  
    logging.debug("Completed fetching all public IP addresses associated with DNS records.")  
    return {'public_ips': public_ips}  
  
# Example usage  
if __name__ == '__main__':  
    try:  
        public_ips_json = get_cloudflare_ips()  
        print(public_ips_json)  
    except Exception as e:  
        logging.error(f'Failed to search for public IPs: {e}')  