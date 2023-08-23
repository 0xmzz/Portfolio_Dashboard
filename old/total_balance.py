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

def store_data(data=None):
    if data is not None:
        data_store['stored_data'] = data
    else:
        return data_store.get('stored_data', None)

def main():
    st.title("DeBank Portfolio Dashboard")
    
    # Input for Ethereum address
    address = st.text_input("Enter Ethereum Address:", "")
    
    # Buttons to refresh and get data from the API or pull from cache
    refresh_data = st.button("Refresh Data")
    pull_from_cache = st.button("Pull from Cache")
    
    if refresh_data:
        data = fetch_total_balance(address)
        
        if data:
            df = process_balance_data(data)
            
            # Store the df in cache
            store_data(df)
            
            st.write(df)
            
            # Pie chart visualization
            fig = px.pie(df, values='USD Value', names='Chain Name', title='Portfolio Distribution by Chain')
            st.plotly_chart(fig)
            
            # CSV download link
            csv = df.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="portfolio_data.csv">Download CSV File</a>'
            st.markdown(href, unsafe_allow_html=True)
        else:
            st.write("No data found for the provided address.")
            
    elif pull_from_cache:
        # Retrieve the df from cache
        cached_data = store_data()
        if cached_data is not None:
            st.write(cached_data)
            
            # Pie chart visualization
            fig = px.pie(cached_data, values='USD Value', names='Chain Name', title='Portfolio Distribution by Chain')
            st.plotly_chart(fig)
            
            # CSV download link
            csv = cached_data.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="portfolio_data.csv">Download CSV File</a>'
            st.markdown(href, unsafe_allow_html=True)
        else:
            st.write("No cached data found. Please click 'Refresh Data' first.")

if __name__ == "__main__":
    main()
