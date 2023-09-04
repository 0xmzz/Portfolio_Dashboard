import requests
from utils import DEBANK_API_URL, headers  # Assuming headers are defined in utils.py
import data_processing

DEBUG = False # Set to False to disable debug statements

def debug_print(msg):
    if DEBUG:
        print(msg)

def fetch_data_from_api(url, address=None):
    debug_print(f"Fetching data from {url}...")
    params = {}
    if address:
        params['id'] = address
    try:
        response = requests.get(url, headers=headers, params=params)
        debug_print(f"Data fetched: {response.json()}")
        return response.json()
    except Exception as e:
        debug_print(f"Error fetching data: {e}")
        return []

def fetch_all_token_list(address):
    debug_print(f"Fetching all tokens for address: {address}...")
    url = f"{DEBANK_API_URL}/v1/user/all_token_list"
    return fetch_data_from_api(url, address=address)

def fetch_total_balance(address):
    url = f"{DEBANK_API_URL}/v1/user/total_balance"
    return fetch_data_from_api(url, address=address)

def fetch_aggregated_data(addresses):
    debug_print(f"Fetching aggregated data for addresses: {addresses}...")
    aggregated_data = []
    token_data_list = []

    for address in addresses:
        chain_balance_data = fetch_total_balance(address)
        if chain_balance_data:
            processed_data = data_processing.process_balance_data(chain_balance_data)
            if processed_data is not None:
                aggregated_data.append(processed_data)

        token_data = fetch_all_token_list(address)
        if token_data:
            processed_token_data = data_processing.process_all_token_list(token_data)
            if processed_token_data is not None and not processed_token_data.empty:
                token_data_list.append(processed_token_data)

    debug_print(f"Aggregated Data: {aggregated_data}")
    debug_print(f"Token Data List: {token_data_list}")

    return aggregated_data, token_data_list
