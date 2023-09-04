import streamlit as st
from api_calls import fetch_total_balance, fetch_all_token_list
from data_processing import process_all_token_list, process_balance_data
from utils import check_schema
from database import save_addresses_to_id, load_addresses_from_id, load_all_user_ids, store_total_balance_data, store_all_token_list_data, load_saved_data, initialize_db
import json
import datetime
import sqlite3

DB_FILE = 'debank_data.db'




# Load the expected schema from the config file
with open('config/schema_config.json', 'r') as f:
    expected_schema = json.load(f)

def store_all_token_list_data(user_id, address, token_data_df):
    try:
        with sqlite3.connect(DB_FILE) as conn:
            token_data_df.to_sql('all_token_list_data', conn, if_exists='replace', index=False)
            # Add code to associate this data with user_id and address
    except Exception as e:
        print(f"Error in store_all_token_list_data: {e}")
# Function to update a single address (for testing)
def update_database_for_testing(address):
    st.write(f"Updating database for address {address}...")
    try:
        # Fetch and process chain data (total_balance)
        raw_balance_data = fetch_total_balance(address)
        st.write("### Raw Chain Data (Total Balance)")
        

        processed_balance_data = process_balance_data(raw_balance_data)  # Process the data

        # Check the schema for balance data
        st.write("### Processed Chain Data")
        if processed_balance_data is not None and not processed_balance_data.empty:
            st.write(processed_balance_data)
            if not check_schema(processed_balance_data, expected_schema['chain_data']):
                st.error("Schema mismatch for chain data!")
            st.write("### Processed Chain Data")
            st.write(processed_balance_data)

        # Fetch and process token data (all_token_list)
        raw_token_data = fetch_all_token_list(address)
        st.write("### Raw Token Data")
        # st.write(raw_token_data[:5])  # Display only the head of the data

        processed_token_data = process_all_token_list(raw_token_data, expected_schema)  # Process the data

        # Check Data Types
        # st.write("Data Types:", processed_token_data.dtypes)

        # Check the schema for token data
        if processed_token_data is not None and not processed_token_data.empty:
            if not check_schema(processed_token_data, expected_schema['all_token_list']):
                st.error("Schema mismatch for token data!")
            st.write("### Processed Token Data")
            # st.write(processed_token_data.head())  # Display only the head of the data

            # Save data to database
            user_id = "some_user_id"  # Replace with actual user ID
            save_addresses_to_id(user_id, address)
            
            # Use the new storage methods here
            store_total_balance_data(user_id, address, processed_balance_data)
            store_all_token_list_data(user_id, address, processed_token_data)

            st.success(f"Database updated for address {address}")

    except Exception as e:
        st.error(f"An error occurred here: {e}")

# Function to update all addresses in the database
def update_all_databases():
    try:
        user_ids = load_all_user_ids()
        for user_id in user_ids:
            addresses = load_addresses_from_id(user_id)
            for address in addresses:
                update_database_for_testing(address)
        st.success("All databases updated.")
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Streamlit UI
def main():
    st.title('Database Loader')
# Add a button to initialize the database
    if st.sidebar.button('Initialize Database'):
        initialize_db()
        with open('last_init_time.txt', 'w') as f:
            f.write(str(datetime.datetime.now()))
        st.sidebar.success('Database initialized.')

    # Display the last time the database was initialized
    try:
        with open('last_init_time.txt', 'r') as f:
            last_init_time = f.read()
        st.sidebar.write(f"Last initialized: {last_init_time}")
    except FileNotFoundError:
        st.sidebar.write("Database not initialized yet.")
    # Streamlit text input to get Ethereum address
    address = st.text_input("Enter Ethereum Address:", value="0x353d566af2b571f6ade5cc9f7a91422f6f738098", type="default")

    # Streamlit button to trigger update for a single address (for testing)
    if st.button('Update Database for Entered Address'):
        if address:
            update_database_for_testing(address)
        else:
            st.warning("Please enter an Ethereum address.")

    # Streamlit button to trigger update for all addresses
    if st.button('Update all Addresses in Database'):
        update_all_databases()

if __name__ == '__main__':
    main()

    st.title('Database Loader')

    