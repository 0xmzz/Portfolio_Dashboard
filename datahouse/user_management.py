import streamlit as st
from database import (create_user_id, fetch_user_ids, add_address_to_user, 
                      fetch_addresses_for_user, delete_user_id, delete_address_for_user)

def user_management_app():
    st.title('User Management')

    # Create a new User ID
    new_user_id = st.text_input("Enter a new User ID:")
    if st.button('Create User ID'):
        if new_user_id:
            create_user_id(new_user_id)
            st.success(f"User ID {new_user_id} created.")
        else:
            st.warning("Please enter a User ID.")

    # Select an existing User ID
    user_ids = fetch_user_ids()
    selected_user_id = st.selectbox("Select a User ID:", user_ids)

    # Add an address to the selected User ID
    new_address = st.text_input("Enter an address to add to the selected User ID:")
    if st.button('Add Address'):
        if new_address:
            add_address_to_user(selected_user_id, new_address)
            st.success(f"Address {new_address} added to User ID {selected_user_id}.")
        else:
            st.warning("Please enter an address.")

    # Display addresses associated with the selected User ID
    addresses = fetch_addresses_for_user(selected_user_id)
    st.write("Addresses associated with the selected User ID:")
    for address in addresses:
        st.write(address)

    # Delete an address from the selected User ID
    delete_address = st.selectbox("Select an address to delete:", addresses)
    if st.button('Delete Address'):
        delete_address_for_user(selected_user_id, delete_address)
        st.success(f"Address {delete_address} deleted from User ID {selected_user_id}.")

    # Delete a User ID
    if st.button('Delete User ID'):
        delete_user_id(selected_user_id)
        st.success(f"User ID {selected_user_id} deleted.")

if __name__ == '__main__':
    user_management_app()
