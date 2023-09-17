import streamlit as st
import json
import pandas as pd
from decimal import Decimal

from database import fetch_user_ids, load_data_from_file, save_raw_data_for_user_to_file, load_data_from_file_and_save_to_db

def to_decimal(val):
    return Decimal(str(val))

def handle_data_loading():
    user_id = st.sidebar.selectbox("Select User ID", fetch_user_ids(), key="user_id_selectbox")

    # Load user token blacklist if available
    try:
        with open(f'data/token_blacklist_{user_id}.json', 'r') as f:
            token_blacklist = json.load(f)
    except FileNotFoundError:
        token_blacklist = {}

    # Load data from file
    if st.sidebar.button('Load Data from File'):
        try:
            filename = f"data/raw_api_data_{user_id}.json"
            all_data = load_data_from_file(filename)
            
            for address, data in all_data.items():
                # Extract raw_balance_data
                raw_balance_data = data.get("raw_balance_data", [])

                # Extract chain_list from raw_balance_data
                chain_list = raw_balance_data.get("chain_list", [])
                
                balance_data_list = []
                for balance in chain_list:
                    if Decimal(balance["usd_value"]) > 0:
                        balance_data_list.append({
                            'chain_name': balance.get("name"),
                            'usd_value': balance["usd_value"]
                        })
                
                if balance_data_list:
                    st.subheader(f"Balance Data for Address: {address}")
                    st.write(pd.DataFrame(balance_data_list))
                
                # Fetch raw_token_data for each address
                raw_token_data = data.get("raw_token_data", [])
                if not isinstance(raw_token_data, list):
                    st.error(f"Unexpected raw_token_data format for address {address}: {type(raw_token_data)}")
                    continue

                all_tokens = [token.get('name') for token in raw_token_data]
                st.subheader(f"Token selection for Address: {address}")
                
                # Multi-select implementation
                blacklisted_tokens = st.multiselect(
                    f'Select tokens to hide for {address}:',
                    all_tokens,
                    default=token_blacklist.get(address, [])
                )
                
                # Save the blacklisted tokens for persistence
                token_blacklist[address] = blacklisted_tokens

                verified_token_data = []
                total_usd_value_for_address = Decimal(0)

                for token in raw_token_data:
                    token_name = token.get('name')
                    
                    # Skip blacklisted tokens
                    if token_name in blacklisted_tokens:
                        continue
                    
                    amount = token.get("amount", 0)
                    price_value = token.get("price", 0)
                    usd_value = Decimal(str(float(amount))) * Decimal(str(float(price_value)))
                    total_usd_value_for_address += usd_value

                    verified_token_data.append({
                        'chain_name': token.get("chain"),
                        'name': token_name,
                        'amount': amount,
                        'usd_value': usd_value,
                        'price': price_value
                    })
                
                # Display the token data for the address
                if verified_token_data:
                    st.subheader(f"Token Data for Address: {address} (Total USD Value: ${total_usd_value_for_address:.2f})")
                    st.write(pd.DataFrame(verified_token_data))

            st.sidebar.success(f"Data loaded from file {filename}")

            # Save the updated token blacklist at the end
            with open(f'data/token_blacklist_{user_id}.json', 'w') as f:
                json.dump(token_blacklist, f)

        except FileNotFoundError:
            st.error(f"File {filename} not found. Please ensure the data file exists.")
        except Exception as e:
            import traceback
            st.error(traceback.format_exc())  # Print the traceback to the Streamlit app

    if st.sidebar.button('Save Raw Data for User to File'):
        save_raw_data_for_user_to_file(user_id)
        st.sidebar.write(f"Selected User ID: {user_id}")
        st.sidebar.success(f'Raw data for user {user_id} saved to file.')

    if st.sidebar.button('Load and Save Raw Data from file to DB for user'):
        load_data_from_file_and_save_to_db(user_id)
        st.sidebar.write(f"Selected User ID: {user_id}")
        st.sidebar.success(f'Raw data for user {user_id} saved to file.')
