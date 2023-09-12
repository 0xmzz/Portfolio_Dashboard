import psycopg2
import json
from api_calls import fetch_total_balance, fetch_all_token_list
import pandas as pd
import os
from utils import to_decimal
from sqlalchemy import create_engine
from decouple import config

# Load environment variables from .env file
DATABASE_URL = config('DATABASE_URL')



engine = create_engine(DATABASE_URL, echo=True)


def ensure_data_directory():
    if not os.path.exists('data'):
        os.makedirs('data')

def execute_query(query, params=()):
    with psycopg2.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()

def execute_query_with_result(query, params=()):
    with psycopg2.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

def initialize_db():
    execute_query('''
        CREATE TABLE IF NOT EXISTS users (
            user_id VARCHAR PRIMARY KEY,
            addresses VARCHAR
        );
    ''')
    execute_query('''
        CREATE TABLE IF NOT EXISTS total_balance_data (
            user_id VARCHAR,
            address VARCHAR,
            timestamp TIMESTAMP,
            chain_data VARCHAR
        );
    ''')
    execute_query('''
        CREATE TABLE IF NOT EXISTS all_token_list_data (
            user_id VARCHAR,
            address VARCHAR,
            timestamp TIMESTAMP,
            id VARCHAR,
            chain VARCHAR,
            name VARCHAR,
            symbol VARCHAR,
            display_symbol VARCHAR,
            optimized_symbol VARCHAR,
            decimals INTEGER,
            logo_url VARCHAR,
            protocol_id VARCHAR,
            price REAL,
            price_24h_change REAL,
            is_verified BOOLEAN,
            is_core BOOLEAN,
            is_wallet BOOLEAN,
            time_at REAL,
            amount REAL,
            raw_amount REAL,
            raw_amount_hex_str VARCHAR
        );
    ''')

def fetch_user_ids():
    return [row[0] for row in execute_query_with_result("SELECT user_id FROM users")]

def create_user_id(user_id, addresses):
    addresses_json = json.dumps(addresses)
    execute_query('INSERT INTO users (user_id, addresses) VALUES (?, ?)', (user_id, addresses_json))

def save_addresses_to_id(user_id, addresses):
    execute_query('INSERT OR REPLACE INTO users (user_id, addresses) VALUES (?, ?)', (user_id, json.dumps(addresses)))

def delete_user_id(user_id):
    execute_query('DELETE FROM users WHERE user_id = ?', (user_id,))

def add_address_to_user(user_id, address):
    existing_addresses = load_addresses_from_id(user_id)
    existing_addresses.append(address)
    save_addresses_to_id(user_id, existing_addresses)

def remove_address_from_user(user_id, address):
    existing_addresses = load_addresses_from_id(user_id)
    if address in existing_addresses:
        existing_addresses.remove(address)
    save_addresses_to_id(user_id, existing_addresses)

def add_address_for_user(user_id, new_address):
    try:
        current_addresses = fetch_addresses_for_user(user_id)
        if new_address in current_addresses:
            print(f"Address {new_address} already exists for user {user_id}.")
            return
        current_addresses.append(new_address)
        save_addresses_to_id(user_id, current_addresses)
        print(f"Address {new_address} added for user {user_id}.")
    except Exception as e:
        print(f"Error in add_address_for_user: {e}")

def delete_address_for_user(user_id, address):
    addresses = fetch_addresses_for_user(user_id)
    if address in addresses:
        addresses.remove(address)
        save_addresses_to_id(user_id, addresses)

def load_addresses_from_id(user_id):
    result = execute_query_with_result('SELECT addresses FROM users WHERE user_id = ?', (user_id,))
    return json.loads(result[0][0]) if result else []

def fetch_addresses_for_user(user_id):
    result = execute_query_with_result('SELECT addresses FROM users WHERE user_id = ?', (user_id,))
    return json.loads(result[0][0]) if result else []

def load_all_user_ids():
    return [row[0] for row in execute_query_with_result("SELECT user_id FROM users")]

def update_all_databases():
    user_ids = load_all_user_ids()
    for user_id in user_ids:
        addresses = load_addresses_from_id(user_id)
        for address in addresses:
            # Here, you can call the function to update the database for each address.
            # For example: update_database_for_testing(address)
            pass

def load_data_from_file(filename):
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error reading/parsing JSON: {e}")
        return None



    except FileNotFoundError:
        print(f"File {filename} not found in {os.getcwd()}")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file {filename}")
        return None

def save_raw_data_for_user_to_file(user_id):
    ensure_data_directory()
    addresses = fetch_addresses_for_user(user_id)
    
    all_data = {}
    for address in addresses:
        raw_balance_data = fetch_total_balance(address)
        raw_token_data = fetch_all_token_list(address)
        
        combined_data = {
            "raw_balance_data": raw_balance_data,
            "raw_token_data": raw_token_data
        }
        all_data[address] = combined_data
    
    filename = f"data/raw_api_data_{user_id}.json"
    with open(filename, "w") as f:
        json.dump(all_data, f)

def store_total_balance_data(user_id, address, raw_balance_data):
    # If raw_balance_data is not already in DataFrame format, convert it to one.
    if not isinstance(raw_balance_data, pd.DataFrame):
        raw_balance_data_df = pd.DataFrame([raw_balance_data])  # or any other appropriate conversion
    else:
        raw_balance_data_df = raw_balance_data
    
    raw_balance_data_df['user_id'] = user_id
    raw_balance_data_df['address'] = address
    with engine.connect() as conn:  # Use the SQLAlchemy engine to create a connection
        raw_balance_data_df.to_sql('total_balance_data', conn, if_exists='replace', index=False)

def store_all_token_list_data(user_id, address, token_data_df):
    token_data_df['raw_amount'] = token_data_df['raw_amount'].apply(to_decimal)

    try:
        for col in ['raw_amount']:
            token_data_df[col] = token_data_df[col].astype(str)

        token_data_df['user_id'] = user_id
        token_data_df['address'] = address
        with psycopg2.connect(DATABASE_URL) as conn:
            token_data_df.to_sql('all_token_list_data', conn, if_exists='append', index=False)
            conn.commit()
    except Exception as e:
        print(f"Error in store_all_token_list_data: {e}")

def save_raw_data_for_user_to_db(user_id):
    addresses = fetch_addresses_for_user(user_id)
    
    for address in addresses:
        raw_balance_data = fetch_total_balance(address)
        raw_token_data = fetch_all_token_list(address)
        
        # Now, store these raw data into your PostgreSQL database
        store_total_balance_data(user_id, address, raw_balance_data)
        store_all_token_list_data(user_id, address, raw_token_data)

def load_data_from_file_and_save_to_db(user_id):
    filename = f"data/raw_api_data_{user_id}.json"
    with open(filename, "r") as f:
        all_data = json.load(f)
        
    for address, combined_data in all_data.items():
        raw_balance_data = combined_data["raw_balance_data"]
        raw_token_data = combined_data["raw_token_data"]
        
        # Now, store these raw data into your PostgreSQL database
        store_total_balance_data(user_id, address, raw_balance_data)
        store_all_token_list_data(user_id, address, raw_token_data)

def cleanup_json_file(user_id):
    filename = f"data/raw_api_data_{user_id}.json"
    try:
        os.remove(filename)
        print(f"Successfully deleted {filename}.")
    except Exception as e:
        print(f"Error deleting file {filename}: {e}")


if __name__ == "__main__":
    initialize_db()
