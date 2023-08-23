import requests
from utils import DEBANK_API_URL, headers

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
