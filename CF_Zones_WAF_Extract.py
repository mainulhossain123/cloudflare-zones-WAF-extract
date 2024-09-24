import os
import requests
import csv
from datetime import datetime
import time

# Create a session to reuse HTTP connections
session = requests.Session()

def get_zones(api_key, page, per_page):
    url = "https://api.cloudflare.com/client/v4/zones"
    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    params = {
        "page": page,
        "per_page": per_page
    }
    retries = 3
    for _ in range(retries):
        response = session.get(url, headers=headers, params=params) 
        if response.status_code == 200:
            data = response.json()
            if data['success'] and data['result']:
                dxp_zones = [zone for zone in data['result'] if zone['account']['name'] == 'DXP Customers']
                return True, dxp_zones
        else:
            print("Failed to fetch zones:", response.text)
            time.sleep(5)  # Wait for 5 seconds before retrying
    return False, None

def get_firewall_custom_rules(zone_id, api_key):
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/rulesets/phases/http_request_firewall_custom/entrypoint"
    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    
    retries = 3  # Number of retries in case of failure
    for _ in range(retries):
        response = session.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            continue
    
    return None

def write_to_csv(zone_data, api_key):
    current_date = datetime.now().strftime("%Y-%m-%d")
    filename = f'/app/firewall_custom_rules_{current_date}.csv'  # Save file in /app directory in Docker
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        zone_name = zone_data['name']
        zone_id = zone_data['id']
        zone_rules = get_firewall_custom_rules(zone_id, api_key)
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

# Example usage
if __name__ == "__main__":
    api_key = os.getenv('API_KEY')  # Get API token from environment variable

    page = 1
    per_page = 1000
    retry_delay = 1  # Initial delay time
    while True:
        success, zones = get_zones(api_key, page, per_page)
        if success:
            if zones:
                for zone in zones:
                    write_to_csv(zone, api_key)
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
