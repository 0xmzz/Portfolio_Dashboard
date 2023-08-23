import requests
import os
from dotenv import load_dotenv
import pandas as pd
from main import DEBANK_API_URL

# Load environment variables from .env file
load_dotenv()

# Get the API key from the environment variable
DEBANK_KEY = os.getenv("DEBANK_API_KEY")

headers = {
    "accept": "application/json",
    "AccessKey": DEBANK_KEY,
}

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

def fetch_chain_balance(address, chain):
     
    response = requests.get(f"{DEBANK_API_URL}/v1/user/token_list?id={address}&chain_id={chain}", headers=headers)
                 
    # Print raw response data
    print(response.text)
    
    if response.status_code != 200:
        print(f"Error fetching balance for {chain}. Status code: {response.status_code}")
        return None
    
    data = response.json()
    return data
# Process the raw data and create a DataFrame
def process_data(data):
    extracted_data = []
    for entry in data:
        token_name = entry.get('name', None)
        token_symbol = entry.get('symbol', None)
        token_amount = entry.get('amount', None)
        token_price = entry.get('price', None)

        extracted_data.append({
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
    chain = normalized_chain_value("eth")  # You can modify this to test other chains
    raw_data = fetch_chain_balance(address, chain)  
    # Process the raw data
    df = process_data(raw_data)
    
    # Print the DataFrame
    print(df)

    # Optionally, save the DataFrame to a CSV for further inspection
    df.to_csv('token_data.csv', index=False)