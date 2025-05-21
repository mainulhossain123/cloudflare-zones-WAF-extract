import os
import requests
import csv
from datetime import datetime, timezone
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Create a session to reuse HTTP connections
session = requests.Session()

def get_zones(api_key, page, per_page, account_name):
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
                # Filter zones based on the user-specified account name
                dxp_zones = [zone for zone in data['result'] if zone['account']['name'] == account_name]
                return True, dxp_zones
        else:
            print(f"Failed to fetch zones for page {page}: {response.text}")
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
            time.sleep(1)
            continue
    return None

def write_to_csv(zone_data, api_key, rule_action, filename):
    # Open the CSV file in append mode and write data
    with open(filename, mode='a', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        
        # Now fetch rules and write to CSV
        zone_name = zone_data['name']
        zone_id = zone_data['id']
        zone_rules = get_firewall_custom_rules(zone_id, api_key)
        
        if zone_rules and 'result' in zone_rules:
            result = zone_rules['result']
            # Filter rules based on user-specified action
            filtered_rules = [rule for rule in result['rules'] if rule['action'] == rule_action]
            for rule in filtered_rules:
                # Write each rule's data to the CSV
                csv_writer.writerow([
                    zone_name, 
                    rule['id'], 
                    rule['version'], 
                    rule['action'], 
                    rule['expression'], 
                    rule['description'], 
                    rule['last_updated'], 
                    rule['enabled']
                ])
                print(f"Zone Name: {zone_name}, Rule ID: {rule['id']}, Action: {rule['action']}")

def process_zone(zone, api_key, rule_action, filename):
    write_to_csv(zone, api_key, rule_action, filename)

if __name__ == "__main__":
    api_key = os.getenv('API_KEY')
    account_name = os.getenv('ACCOUNT_NAME', 'DXP Customers')  # Default to 'DXP Customers'
    rule_action = os.getenv('RULE_ACTION', 'skip')  # Default to 'skip'

    current_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    filename = f'/app/firewall_custom_rules_{current_date}.csv'

    # Write the headers once at the start
    with open(filename, mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([
            "Zone Name", "Rule ID", "Version", "Action", 
            "Expression", "Description", "Last Updated", "Enabled"
        ])

    page = 1
    per_page = 1000
    retry_delay = 1
    all_zones = []

    # Fetch zones in parallel with account name filtering
    while True:
        success, zones = get_zones(api_key, page, per_page, account_name)
        if success:
            if zones:
                all_zones.extend(zones)
                page += 1
                time.sleep(0.5)  # Lower delay if API allows it
            else:
                print("No more zones to process.")
                break
        else:
            retry_delay *= 2
            print(f"Retrying in {retry_delay} seconds due to errors.")
            time.sleep(retry_delay)
            if retry_delay > 60:
                print("Maximum retry delay reached. Exiting.")
                break

    # Process zones using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=10) as executor:  # Adjust max_workers based on the rate limit
        future_to_zone = {executor.submit(process_zone, zone, api_key, rule_action, filename): zone for zone in all_zones}
        for future in as_completed(future_to_zone):
            zone = future_to_zone[future]
            try:
                future.result()
            except Exception as e:
                print(f"Error processing zone {zone['name']}: {e}")
