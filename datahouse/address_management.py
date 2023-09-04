import streamlit as st
from api_calls import fetch_total_balance
from data_standardization import standardize_and_flatten_protocol_data
from database import save_raw_json_to_db, save_addresses_to_id, load_addresses_from_id, load_all_user_ids

def manage_addresses(key_suffix=""):
    """
    Manage Ethereum addresses for a user ID.
    Returns a list of addresses.
    """
    all_user_ids = load_all_user_ids()
    all_user_ids.append("Create New")
    
    # Adding a unique key for the selectbox
    selected_user_id = st.selectbox("Select User ID", all_user_ids, key=f"user_id_selectbox_{key_suffix}")
    
    if selected_user_id == "Create New":
        new_user_id = st.text_input("Enter a new User ID:")
        if new_user_id:
            selected_user_id = new_user_id

    saved_addresses = load_addresses_from_id(selected_user_id)
    
    addresses = []
    num_addresses = st.slider("Number of addresses", 1, 10, len(saved_addresses) if saved_addresses else 1)
    
    for i in range(num_addresses):
        address = st.text_input(f"Address {i+1}:", saved_addresses[i] if saved_addresses and i < len(saved_addresses) else "")
        if address:
            addresses.append(address.strip())

    if st.button("Save Addresses"):
        save_addresses_to_id(selected_user_id, addresses)
        st.write(f"Addresses saved for {selected_user_id}!")

    return addresses