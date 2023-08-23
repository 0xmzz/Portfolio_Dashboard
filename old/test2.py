import requests
import os
import pandas as pd
from dotenv import load_dotenv
import base64
import plotly.express as px
import streamlit as st

chains = ["arb", "avax", "bsc", "eth", "ftm", "matic", "metis", "op"]

# Load environment variables from .env file
load_dotenv()

# Get the API key from the environment variable
DEBANK_KEY = os.getenv("DEBANK_API_KEY")

DEBANK_API_URL = "https://pro-openapi.debank.com"

headers = {
    "accept": "application/json",
    "AccessKey": DEBANK_KEY,
}

# Fetch portfolio data from DeBank API



def normalized_chain_value(chain):
    vals = dict(
        arb="arbitrum",
        avax="avalanche",
        bsc="binancesc",
        eth="ethereum",
        ftm="fantom",
        matic="polygon",
        metis="metis",
        op="optimism",
    )
    vals_with_normalized = vals.copy()
    for _, v in vals.items():
        vals_with_normalized[v] = v
    return vals_with_normalized[chain]

def fetch_portfolio(address, chain):
    url = f"https://pro-openapi.debank.com/v1/user/token_list?id={address}&chain_id={chain}"
    response = requests.get(url, headers=headers)
    
    # Check if the response is JSON
    try:
        data = response.json()
    except ValueError:
        print(f"Error fetching data for chain {chain}. Response: {response.text}")
        return None

    chain = normalized_chain_value(chain)
    return data

# Process the raw data and create a DataFrame
def process_data(data):
    extracted_data = []
    for entry in data:
        # token_id = entry.get('id', None)
        token_name = entry.get('name', None)
        token_symbol = entry.get('symbol', None)
        token_amount = entry.get('amount', None)
        token_price = entry.get('price', None)

        extracted_data.append({
            # 'ID': token_id,
            'Name': token_name,
            'Symbol': token_symbol,
            'Amount': token_amount,
            'Price': token_price
        })

    # Create a DataFrame
    df = pd.DataFrame(extracted_data)
    
     # Filter out rows where the product of 'Amount' and 'Price' is less than $10
    df = df[df['Amount'] * df['Price'] >= 10]
    
    return df

# Streamlit app

@st.cache_data(suppress_st_warning=True, allow_output_mutation=True)
def store_data(data=None):
    if data is not None:
        stored_data = data
    else:
        if 'stored_data' not in globals():
            return None
        return stored_data
def main():
    st.title("DeBank Portfolio Dashboard")
    
    # Input for Ethereum address
    address = st.text_input("Enter Ethereum Address:", "")
    refresh_data = st.button("Refresh Data")
    pull_from_cache = st.button("Pull from Cache")
    
    
    # Button to refresh and get data from the API
    
    
    if st.button("Refresh"):
        combined_data = []
        for chain in chains:
            raw_data = fetch_portfolio(address, chain)
            
            # Check if raw_data is not empty and has the 'tokens' key
            if raw_data and 'tokens' in raw_data:
                df = process_data(raw_data['tokens'])
                df['Chain'] = normalized_chain_value(chain)
                combined_data.append(df)
        
        if combined_data:
            combined_df = pd.concat(combined_data, ignore_index=True)
            
            # Store the combined_df in cache
            store_data(combined_df)
            
            st.write(combined_df)
            
            # Pie chart visualization
            fig = px.pie(combined_df, values='Amount', names='Name', title='Portfolio Distribution')
            st.plotly_chart(fig)
            
            # CSV download link
            csv = combined_df.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="portfolio_data.csv">Download CSV File</a>'
            st.markdown(href, unsafe_allow_html=True)
        else:
            st.write("No data found for the provided address.")
    
    # Button to pull data from cache
    if st.button("Pull from Cache"):
        # Retrieve the combined_df from cache
        cached_data = store_data()
        if cached_data is not None:
            st.write(cached_data)
            
            # Pie chart visualization
            fig = px.pie(cached_data, values='Amount', names='Name', title='Portfolio Distribution')
            st.plotly_chart(fig)
            
            # CSV download link
            csv = cached_data.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="portfolio_data.csv">Download CSV File</a>'
            st.markdown(href, unsafe_allow_html=True)
        else:
            st.write("No cached data found. Please click 'Refresh' first.")

if __name__ == "__main__":
    main()
