import os
import json
import logging
from datetime import datetime
from calculate_changes import calculate_changes
from add_ips_to_insightvm_site import add_ips_to_insightvm_site
from remove_ips_from_insightvm_site import remove_ips_from_insightvm_site
from replace_ips_in_shodan_net import replace_ips_in_shodan_net

def get_env_variable(var_name, default=None):
    """ Retrieve environment variables and handle those that may end with double parentheses """
    env_var = os.getenv(var_name, default)
    return env_var[:-1] if env_var and env_var.endswith('))') else env_var

# Set up structured logging  
logging_level = get_env_variable('LOGGING_LEVEL', 'INFO')  # Default to INFO if not set
numeric_level = getattr(logging, logging_level.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError(f'Invalid log level: {logging_level}')
logging.basicConfig(level=numeric_level, format='[%(levelname)s] %(asctime)s, %(message)s', datefmt='%m/%d/%Y %H:%M:%S')

# Environment variables for network names and site IDs  
SHODAN_CLOUDFLARE_NET = get_env_variable('SHODAN_CLOUDFLARE_NET')  
SHODAN_AZURE_AWS_NET = get_env_variable('SHODAN_AZURE_AWS_NET')  
INSIGHTVM_CLOUDFLARE_SITE_ID = get_env_variable('INSIGHTVM_CLOUDFLARE_SITE_ID')  
INSIGHTVM_AZURE_AWS_SITE_ID = get_env_variable('INSIGHTVM_AZURE_AWS_SITE_ID')  
  
changes = calculate_changes(INSIGHTVM_CLOUDFLARE_SITE_ID, INSIGHTVM_AZURE_AWS_SITE_ID,   
                            SHODAN_CLOUDFLARE_NET, SHODAN_AZURE_AWS_NET)  

def log_result(ip, target_location, action, result):
    if 'status' in result and result['status'] == 'success':
        logging.info(f"{ip}, {target_location}, {action}, Success")
        return 'Success'
    else:
        error_message = result.get('message', 'Unknown error')
        logging.error(f"{ip}, {target_location}, {action}, FAILURE, {error_message}")
        return 'FAILURE'
  
def implement_changes():
    successes = 0
    failures = 0

    for change_key, site_id, action in [
        ('insightvm_cloudflare_additions', INSIGHTVM_CLOUDFLARE_SITE_ID, "Addition"),
        ('insightvm_cloudflare_removals', INSIGHTVM_CLOUDFLARE_SITE_ID, "Removal"),
        ('insightvm_insightcloudsec_additions', INSIGHTVM_AZURE_AWS_SITE_ID, "Addition"),
        ('insightvm_insightcloudsec_removals', INSIGHTVM_AZURE_AWS_SITE_ID, "Removal"),
    ]:
        if changes.get(change_key):
            func = add_ips_to_insightvm_site if action == "Addition" else remove_ips_from_insightvm_site
            results = json.loads(func(changes[change_key], site_id))
            for result in results:
                if isinstance(result, dict):
                    res = log_result(result.get('ip'), f"InsightVM Site {site_id}", action, result)
                    if res == 'Success':
                        successes += 1
                    else:
                        failures += 1
                else:
                    logging.error(f"Unexpected result format: {result}")
                    failures += 1

    for change_key, net_name in [
        ('shodan_cloudflare_ips', SHODAN_CLOUDFLARE_NET),
        ('shodan_insightcloudsec_ips', SHODAN_AZURE_AWS_NET),
    ]:
        if changes.get(change_key):
            replace_result = replace_ips_in_shodan_net(changes[change_key], net_name)
            for ip in changes[change_key]:
                if isinstance(replace_result, dict):
                    res = log_result(ip, f"Shodan Net {net_name}", "Replacement", replace_result)
                    if res == 'Success':
                        successes += 1
                    else:
                        failures += 1
                else:
                    logging.error(f"Unexpected result format for replacement: {replace_result}")
                    failures += 1

    logging.info(f"Synchronization completed with {successes} successes and {failures} failures.")

implement_changes()