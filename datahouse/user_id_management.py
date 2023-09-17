import streamlit as st
from database import (load_all_user_ids, fetch_addresses_for_user,
                      add_address_for_user, delete_address_for_user,
                      create_user_id, delete_user_id)


def handle_user_id_management():
    # User ID management
    user_ids = load_all_user_ids()

    if not user_ids:
        st.sidebar.warning("No User IDs found in database.")
    else:
        selected_user_id = st.sidebar.selectbox("Select User ID", user_ids, key="user_id_selectbox")
        
        # Manage Addresses for Selected User ID
        st.sidebar.subheader(f"Manage Addresses for {selected_user_id}")
        st.sidebar.write("Addresses:")
        st.sidebar.write("\n".join(fetch_addresses_for_user(selected_user_id)))

        new_address = st.sidebar.text_input("Add New Address", key="new_address_input")
        if st.sidebar.button("Add Address", key="add_new_address_button"):
            if new_address:
                add_address_for_user(selected_user_id, new_address)
                st.sidebar.success(f"Address {new_address} added for User ID {selected_user_id}")

        address_to_delete = st.sidebar.selectbox("Select an address to delete", fetch_addresses_for_user(selected_user_id), key="address_delete_selectbox")
        if st.sidebar.button("Delete Address", key="delete_address_button"):
            if address_to_delete:
                delete_address_for_user(selected_user_id, address_to_delete)
                st.sidebar.success(f"Address {address_to_delete} deleted for User ID {selected_user_id}")

    # Create New User ID
    st.sidebar.subheader("Create New User ID")

    # Check session state for user ID input, and initialize if not present
    if 'new_user_id_input' not in st.session_state:
        st.session_state.new_user_id_input = ''
        # print("Initialized session state for new_user_id_input")

    user_id_input = st.sidebar.text_input("Enter new User ID alias", st.session_state.new_user_id_input)
    # print(f"Text input value after instantiation: {user_id_input}")

    # Now update the session state
    st.session_state.new_user_id_input = user_id_input 
    # print(f"Updated session state with: {st.session_state.new_user_id_input}")


    # Check session state for addresses input, and initialize if not present
    if 'addresses_input' not in st.session_state:
        st.session_state.addresses_input = ''

    addresses_textarea = st.sidebar.text_area("Enter addresses (one per line):", st.session_state.addresses_input)
    st.session_state.addresses_input = addresses_textarea  # Update session state with textarea value

    # Filter out empty addresses
    addresses = [address.strip() for address in addresses_textarea.split("\n") if address.strip()]


    # print(f"User ID (from input): {user_id_input}")
    # print(f"Addresses (from textarea): {addresses_textarea}")

    if st.sidebar.button("Save New User ID and Addresses", key="create_user_id_button"):
        # print("Button pressed!")
        # print(f"User ID (from session state): {st.session_state.new_user_id_input}")
        # print(f"Addresses (from session state): {addresses}")

        if st.session_state.new_user_id_input and addresses:
            create_user_id(st.session_state.new_user_id_input, addresses)
            st.sidebar.success(f"User ID {st.session_state.new_user_id_input} created with addresses.")
        elif not addresses:
            st.sidebar.warning("Please provide at least one valid address.")
        else:
            st.sidebar.warning("Please provide both User ID and at least one address.")

    # Delete User ID
    if st.sidebar.button("Delete Selected User ID", key="delete_user_id_button"):
        delete_user_id(selected_user_id)
        st.sidebar.success(f"User ID {selected_user_id} deleted.")
