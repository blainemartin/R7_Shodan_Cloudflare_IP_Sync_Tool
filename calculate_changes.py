import json
import logging
from get_insightcloudsec_ips import get_insightcloudsec_ips
from get_insightvm_site_contents import get_insightvm_site_contents
from get_shodan_net_contents import get_shodan_net_contents

# Set up structured logging with a specific format for later log collection
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Custom logger for structured JSON logging
class StructuredLogger(logging.LoggerAdapter):
    def log(self, level, msg, *args, **kwargs):
        if self.isEnabledFor(level):
            msg, kwargs = self.process(msg, kwargs)
            self.logger.log(level, msg, *args, **kwargs)

    def process(self, msg, kwargs):
        # Include the log level name (e.g., "DEBUG", "INFO") in the JSON output
        level_name = logging.getLevelName(self.logger.getEffectiveLevel())
        return json.dumps({'level': level_name, 'message': msg, **kwargs}), {}

logger = StructuredLogger(logging.getLogger(__name__), {})

def calculate_changes(insightvm_azure_aws_site_id, shodan_azure_aws_net):
    logger.debug("Starting to calculate changes between sources and targets.")

    logger.debug("Fetching IPs from InsightCloudSec API.")
    insightcloudsec_ips_data = get_insightcloudsec_ips()
    insightcloudsec_ips = {ip['IP Address'] for ip in json.loads(insightcloudsec_ips_data)}
    logger.debug('InsightCloudSec API response received', extra={'response': insightcloudsec_ips_data})

    logger.debug("Fetching IPs from InsightVM for Azure/AWS site.")
    insightvm_insightcloudsec_ips_data = get_insightvm_site_contents(insightvm_azure_aws_site_id)
    insightvm_insightcloudsec_ips = set(json.loads(insightvm_insightcloudsec_ips_data))
    logger.debug('InsightVM Azure/AWS site contents received', extra={'response': insightvm_insightcloudsec_ips_data})

    logger.debug("Fetching IPs from Shodan for Azure/AWS network.")
    shodan_insightcloudsec_ips_data = get_shodan_net_contents(shodan_azure_aws_net)
    shodan_insightcloudsec_ips = set(json.loads(shodan_insightcloudsec_ips_data)['ip'])
    logger.debug('Shodan Azure/AWS network contents received', extra={'response': shodan_insightcloudsec_ips_data})

    # Calculate additions and removals
    insightvm_insightcloudsec_additions = insightcloudsec_ips - insightvm_insightcloudsec_ips
    insightvm_insightcloudsec_removals = insightvm_insightcloudsec_ips - insightcloudsec_ips

    # Log results
    logger.debug("Calculated changes successfully.", extra={'changes': {
        "insightvm_insightcloudsec_additions": list(insightvm_insightcloudsec_additions) if insightvm_insightcloudsec_additions else None,
        "insightvm_insightcloudsec_removals": list(insightvm_insightcloudsec_removals) if insightvm_insightcloudsec_removals else None,
    }})

    return {
        "insightvm_insightcloudsec_additions": list(insightvm_insightcloudsec_additions) if insightvm_insightcloudsec_additions else None,
        "insightvm_insightcloudsec_removals": list(insightvm_insightcloudsec_removals) if insightvm_insightcloudsec_removals else None,
    }

if __name__ == '__main__':
    # Example identifiers for network names and site IDs
    SHODAN_AZURE_AWS_NET = "Cloud Public IPs (Azure&AWS)"
    INSIGHTVM_AZURE_AWS_SITE_ID = "200"

    # Call the function with the specified identifiers
    try:
        changes = calculate_changes(INSIGHTVM_AZURE_AWS_SITE_ID, SHODAN_AZURE_AWS_NET)
        logger.debug('Calculated changes successfully', extra={'changes': changes})
    except Exception as e:
        logger.error('Failed to calculate changes', extra={'error': str(e)})
