import requests
import os
import pandas as pd
from dotenv import load_dotenv
import base64
import plotly.express as px
import streamlit as st



# Load environment variables from .env file
load_dotenv()

# Get the API key from the environment variable
DEBANK_KEY = os.getenv("DEBANK_API_KEY")

DEBANK_API_URL = "https://pro-openapi.debank.com"

headers = {
    "accept": "application/json",
    "AccessKey": DEBANK_KEY,
}

data_store = {}

def fetch_total_balance(address):
    url = f"{DEBANK_API_URL}/v1/user/total_balance?id={address}"
    response = requests.get(url, headers=headers)
    
    try:
        data = response.json()
    except ValueError:
        st.write(f"Error fetching data. Response: {response.text}")
        return None

    return data

def fetch_nft_list(address, chain_id="eth"):
    url = f"{DEBANK_API_URL}/v1/user/nft_list?id={address}&chain_id={chain_id}"
    response = requests.get(url, headers=headers)
    
    try:
        data = response.json()
    except ValueError:
        st.write(f"Error fetching data. Response: {response.text}")
        return None

    return data

def process_balance_data(data):
    chain_list = data.get("chain_list", [])
    extracted_data = []
    for chain in chain_list:
        extracted_data.append({
            'Chain Name': chain.get('name'),
            'USD Value': chain.get('usd_value'),
            'Logo': chain.get('logo_url')
        })

    return pd.DataFrame(extracted_data)

def process_nft_data(data):
    return pd.DataFrame(data)

def store_data(data=None):
    if data is not None:
        st.session_state.stored_data = data
        st.write("Data stored in cache.")  # Debug message
    else:
        cached_data = getattr(st.session_state, 'stored_data', None)
        if cached_data is None:
            st.write("Debug: No data in session state cache.")  # Debug message
        else:
            st.write("Debug: Data retrieved from session state cache.")  # Debug message
        return cached_data



def main():
    st.title("DeBank Portfolio Dashboard")
    
    # Input for Ethereum addresses (multiple addresses separated by commas)
    addresses = st.text_input("Enter Ethereum Addresses (comma-separated):", "")
    address_list = [address.strip() for address in addresses.split(",")]
    
    # Dropdown for API call selection
    api_call_selection = st.selectbox("Select API Call", ["Get Balance", "Get NFT List"])
    
    # Buttons to refresh and get data from the API or pull from cache
    refresh_data = st.button("Refresh Data")
    pull_from_cache = st.button("Pull from Cache")
    
    if refresh_data:
        if api_call_selection == "Get Balance":
            data = fetch_total_balance(address)
            if data:
                df = process_balance_data(data)
        elif api_call_selection == "Get NFT List":
            data = fetch_nft_list(address)
            if data:
                df = process_nft_data(data)
        
        if data:
            # Store the df in cache
            store_data(df)
            
            st.write(df)
            
            # Pie chart visualization for balance data
            if api_call_selection == "Get Balance":
                fig = px.pie(df, values='USD Value', names='Chain Name', title='Portfolio Distribution by Chain')
                st.plotly_chart(fig)
            
            # CSV download link
            csv = df.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="data.csv">Download CSV File</a>'
            st.markdown(href, unsafe_allow_html=True)
        else:
            st.write("No data found for the provided address.")
            
    elif pull_from_cache:
        # Retrieve the df from cache
        cached_data = store_data()
        if cached_data is not None:
            st.write(cached_data)
            
            # Pie chart visualization for balance data
            if api_call_selection == "Get Balance":
                fig = px.pie(cached_data, values='USD Value', names='Chain Name', title='Portfolio Distribution by Chain')
                st.plotly_chart(fig)
            
            # CSV download link
            csv = cached_data.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="data.csv">Download CSV File</a>'
            st.markdown(href, unsafe_allow_html=True)
        else:
            st.write("No cached data found. Please click 'Refresh Data' first.")

import json

def save_data_to_file(data):
    with open('data.json', 'w') as f:
        json.dump(data, f)

def load_data_from_file():
    try:
        with open('data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None


if __name__ == "__main__":
    main()
