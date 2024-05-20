# Cloudflare_Zones_WAF_Extraction_API_Integration
Simple Python script for extracting WAF Bypass rules for Cloudflare zones, generating output to a CSV file

## Note
The code, is for downloading Cloudflare zones WAF information but this can be modified to enter more parameters for more precise information extraction.

## Prerequisites 
* **Python 3.12 or higher**. Download it from https://www.python.org/downloads/
* **IDE** - I personally used Visual Studio Code but it is upto your preference.
* **Libraries - requests**: Run in Terminal of enviornment or in command prompt **pip install requests**
* **Libraries - datetime**: Run in Terminal of enviornment or in command prompt **pip install datetime**
* **Libraries - csv**: Run in Terminal of enviornment or in command prompt **pip install csv**
* **Cloudflare API Key**. You must have the API key enabled with minimum Read permissions from your Cloudflare account.

## Languages, Frameworks and API calls used in the script
The Script uses the following:

- *[Python 3.12.3](https://www.python.org/downloads/release/python-3123/)* as the primary Programming Language.
- *[Visual Studio Code](https://code.visualstudio.com/download)* as the IDE.
- *[Cloudflare V4 Zone entrypoint HTTP firewall request Check](https://developers.cloudflare.com/api/operations/getZoneEntrypointRuleset)* as the secondary endpoint for WAF Authorization header.
- *[Cloudflare V4 Zone list Check](https://developers.cloudflare.com/api/operations/zones-get)* as the primary endpoint for zone Authorization header.
- *[Requests Module](https://pypi.org/project/requests/)* allows us to make HTTP/1.1 request calls.
- *[Datetime Module](https://docs.python.org/3/library/datetime.html)* for usage of current date and time on file naming schemes
- *[Time Module](https://docs.python.org/3/library/time.html)* primarily used in the script to produce delays in the frequency of each request in case of rate-limiting issues
- *[CSV Module](https://docs.python.org/3/library/csv.html)* allows us to write or read CSV files, in this case write all retrieved data to a CSV file.

## Legal
* This code is in no way affiliated with, authorized, maintained, sponsored or endorsed by Cloudflare or any of its affiliates or subsidiaries. This is an independent and unofficial software. Use at your own risk. Commercial use of this code/repo is strictly prohibited.

## Basic Usage

### API_Key Replacement
Simply replace the value in **api_key** with your own API key and run the script. 

#Set your Cloudflare API key
```
api_key = 'YOUR_API_KEY'
```

### User Input
pagination is set for 1000 per page **please set your per_page value as per your needs for better efficiency**. Also a retry delay method is also implemented so that code does not skip or stop in case of rate limiting issues.
```python
page = 1
per_page = 1000
retry_delay = 1  # Initial delay time
while True:
    success, zones = get_zones(api_token, page, per_page)
    if success:
        if zones:
            for zone in zones:
                write_to_csv(zone)
            page += 1
            retry_delay = 1  # Reset the retry delay on successful fetch
            # Introduce a delay between requests to avoid rate limit issues
            time.sleep(1)
        else:
            print("No more zones to process.")
            break
    else:
        # Exponential backoff: Increase delay time exponentially upon rate limit errors
        retry_delay *= 2  # Double the delay time
        print(f"Retrying in {retry_delay} seconds due to errors.")
        time.sleep(retry_delay)
        if retry_delay > 60:  # Maximum delay threshold to prevent infinite looping
            print("Maximum retry delay reached. Exiting.")
            break
```

### Extracted data and CSV File
The data will be saved in a CSV file **firewall_custom_rules_{current_date}.csv**, which you can change to your desire and also include a path for saving if you wish but by default. For the current code the following information below are being written over to the CSV file as shown below. The print statements are there simply for showing progress of the code.
```python
def write_to_csv(zone_data):
    current_date = datetime.now().strftime("%Y-%m-%d")
    filename = f'firewall_custom_rules_{current_date}.csv'
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        zone_name = zone_data['name']
        zone_id = zone_data['id']
        zone_rules = get_firewall_custom_rules(zone_id, api_token)
        if zone_rules and 'result' in zone_rules:
            result = zone_rules['result']
            filtered_rules = [rule for rule in result['rules'] if rule['action'] == 'skip']
            for rule in filtered_rules:
                writer.writerow([zone_name, rule['id'], rule['version'], rule['action'], rule['expression'], rule['description'], rule['last_updated'], rule['enabled']])
                print(f"Zone Name: {zone_name}")
                print(f"Rule ID: {rule['id']}")
                print(f"Rule Version: {rule['version']}")
                print(f"Action: {rule['action']}")
                print(f"Expression: {rule['expression']}")
                print(f"Description: {rule['description']}")
                print(f"Last Updated: {rule['last_updated']}")
                print(f"Rule Status: {rule['enabled']}")
                print("")
```

### Disclaimer
- I have not used multi-threading in this script unlike previous scripts as due to varying number of zones and dataset size, Cloudflare has a tendency to run into ratelimiting issues, particularly with multi-threading for multiple requests, which was causing loss of data.

- I have written this particular code for including all information about CF Zones Bypass rules but that can easily be changed by changiing the "action" rule below
```python
filtered_rules = [rule for rule in result['rules'] if rule['action'] == 'skip']
```
simply remove the filtered line altogether or change the action to your particular needs.
