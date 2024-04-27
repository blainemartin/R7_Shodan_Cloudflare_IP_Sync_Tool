# IP Sync Tool for Rapid7, Shodan, and Cloudflare

## Overview
This project is designed to automate IP address management across various security platforms, including InsightVM, Shodan, Cloudflare, and InsightCloudSec. It handles the synchronization of IP lists between these platforms to ensure consistent and up-to-date IP tracking and threat management.

## Features
- **IP Synchronization**: Automatically adds, removes, and replaces IP addresses across different platforms based on current listings and predefined conditions.
- **Logging**: Detailed logging for auditing and troubleshooting purposes.
- **Error Handling**: Implements robust error handling and rate limiting strategies to ensure reliable operation.

## Dependencies
Ensure you have Python 3.x installed on your system. You can install all required dependencies with:


```bash
pip install -r requirements.txt
```

The main dependency is `requests` for making HTTP requests.

## Configuration
Set up the necessary environment variables and configurations for each platform:

### Cloudflare
- `CLOUDFLARE_API_KEY`: Your Cloudflare API key.
- `CLOUDFLARE_BASE_URL`: Base URL for the Cloudflare API, typically "https://api.cloudflare.com/client/v4".

### InsightCloudSec
- `INSIGHTCLOUDSEC_API_KEY`: Your InsightCloudSec API key.
- `INSIGHTCLOUDSEC_BASE_URL`: Base URL for the InsightCloudSec API.

### InsightVM
- `INSIGHTVM_USERNAME`: Your InsightVM username.
- `INSIGHTVM_PASSWORD`: Your InsightVM password.
- `INSIGHTVM_BASE_URL`: Base URL for the InsightVM API.

### Shodan
- `SHODAN_API_KEY`: Your API key for Shodan.
- `SHODAN_BASE_URL`: Base URL for the Shodan API, typically "https://api.shodan.io".

### Target Locations
- `SHODAN_CLOUDFLARE_NET`: Network ID for Cloudflare in Shodan.
- `SHODAN_AZURE_AWS_NET`: Network ID for Azure and AWS in Shodan.
- `INSIGHTVM_CLOUDFLARE_SITE_ID`: Site ID for Cloudflare in InsightVM.
- `INSIGHTVM_AZURE_AWS_SITE_ID`: Site ID for Azure and AWS in InsightVM.

## Usage
To run the main program, execute:

```bash
python main.py
```

This script will orchestrate the process of fetching, comparing, and updating IP addresses across the platforms specified.

## Contributing
Contributions to this project are welcome! Please fork the repository and submit a pull request with your suggested changes.

## License
This project is licensed under the MIT License - see the LICENSE file for details.


```
