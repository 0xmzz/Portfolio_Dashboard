if tab_selection == "User ID Management":
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

        # If the values are not in the session state, initialize them
        if 'new_user_id_input' not in st.session_state:
            st.session_state.new_user_id_input = ""
        if 'addresses_input' not in st.session_state:
            st.session_state.addresses_input = ""

        # Use the session state variable directly in the widget
        st.sidebar.text_input("Enter new User ID alias", value=st.session_state.new_user_id_input, key="new_user_id_input")
        st.sidebar.text_area("Enter addresses (one per line):", value=st.session_state.addresses_input, key="addresses_input")

        

        # Split by newline and filter out empty addresses
        addresses = [address.strip() for address in st.session_state.addresses_input.split("\n") if address.strip()]

        if st.sidebar.button("Save New User ID and Addresses", key="create_user_id_button"):
            if st.session_state.new_user_id_input and addresses:
                create_user_id(st.session_state.new_user_id_input, addresses)
                st.sidebar.success(f"User ID {st.session_state.new_user_id_input} created with addresses.")

            elif not addresses:
                st.sidebar.warning("Please provide at least one valid address.")
            else:
                st.sidebar.warning("Please provide both User ID and at least one address.")

        # Delete User ID
        if st.sidebar.button("Delete Selected User ID"):
            delete_user_id(selected_user_id)
            st.sidebar.success(f"User ID {selected_user_id} deleted.")
