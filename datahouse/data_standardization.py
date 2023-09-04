import pandas as pd

def standardize_chain_data(chain_data):
    """
    Standardizes the chain data to ensure it has all the required columns.
    """
    required_columns = ['id', 'name', 'usd_value']
    df = pd.DataFrame(chain_data['chain_list'])  # Assuming chain_data is a dictionary with a 'chain_list' key

    for col in required_columns:
        if col not in df.columns:
            df[col] = None  # or other default value

    return df

def standardize_token_data(token_data):
    """
    Standardizes the token data to ensure it has all the required columns.
    """
    required_columns = [
        'id', 'chain', 'name', 'symbol', 'price', 'amount'
    ]
    df = pd.DataFrame(token_data)  # Assuming token_data is a list of dictionaries

    for col in required_columns:
        if col not in df.columns:
            df[col] = None  # or other default value

    return df
