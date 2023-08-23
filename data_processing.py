import pandas as pd

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

