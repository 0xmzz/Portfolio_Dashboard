import requests
import os
import pandas as pd
from dotenv import load_dotenv

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

def fetch_portfolio(address):
  
    response = requests.get(f"https://pro-openapi.debank.com/v1/user/token_list?id={address}&chain_id=eth", headers=headers)
    data = response.json()
    return data

# Process the raw data and create a DataFrame
def process_data(data):
    extracted_data = []
    for entry in data:
        token_id = entry.get('id', None)
        token_name = entry.get('name', None)
        token_symbol = entry.get('symbol', None)
        token_amount = entry.get('amount', None)
        token_price = entry.get('price', None)

        extracted_data.append({
            'ID': token_id,
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

# Main execution
if __name__ == "__main__":
    address = "0x3587b15f7865d4f3f5ca15d29d197bb2f1e6309d"  # You can modify this to test multiple addresses
    raw_data = fetch_portfolio(address)
    
    # Process the raw data
    df = process_data(raw_data)
    
    # Print the DataFrame
    print(df)

    # Optionally, save the DataFrame to a CSV for further inspection
    df.to_csv('token_data.csv', index=False)
