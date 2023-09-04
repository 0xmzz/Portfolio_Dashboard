import pandas as pd
import json
from utils import check_schema
import numpy as np



# Load the expected schema from the config file
with open('config/schema_config.json', 'r') as f:
    expected_schema = json.load(f)

 

DEBUG = True  # Set to False to disable debug statements

def debug_print(msg):
    if DEBUG:
        print(msg)

def process_balance_data(data):
    
    debug_print("Processing balance data...")
    chain_list = data.get('chain_list', [])
    processed_data = []

    for chain in chain_list:
        chain_name = chain.get('name')
        usd_value = chain.get('usd_value', 0)
        processed_data.append({
            'Chain Name': chain_name,
            'USD Value': usd_value
        })

    df = pd.DataFrame(processed_data)
    debug_print(f"Processed data from process_balance_data: {df}")
     # After processing the data, check the schema
     
    if not check_schema(df, expected_schema['chain_data']):
        print("Schema mismatch!")

    
    return df

def process_all_token_list(raw_data, expected_schema):
    try:
        df = pd.DataFrame(raw_data)
        
        # Explicitly convert data types
        df = df.astype({
            'id': 'str',
            'chain': 'str',
            'name': 'str',
            'symbol': 'str',
            # ... other columns
        })

        # Handle None values
        df.fillna(value='', inplace=True)

        # Convert NumPy types to native Python types
        df = df.applymap(lambda x: x.item() if isinstance(x, np.generic) else x)

        return df
    except Exception as e:
        print(f"An error occurred while processing all_token_list data: {e}")
        return None








if __name__ == "__main__":
    # Uncomment the next line to run the debug function
    # debug_process_protocol_data()
    pass

