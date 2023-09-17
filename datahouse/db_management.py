import streamlit as st
from database import (
    fetch_user_ids, load_addresses_from_id,
    update_all_databases, save_raw_data_for_user_to_db,
    load_data_from_file_and_save_to_db, cleanup_json_file
)

def get_database_status():
    """
    Retrieve the status of the PostgreSQL database.
    """
    user_ids = fetch_user_ids()
    data = {}
    for user_id in user_ids:
        data[user_id] = load_addresses_from_id(user_id)
    return data

def handle_db_management():
    """
    Main function for handling the Database Management tab.
    """

    st.title("Database Management")

    all_user_ids = fetch_user_ids()
    selected_user_id = st.sidebar.selectbox("Select User ID:", options=all_user_ids, key="user_id_selectbox")

    # Check Database Status
    if st.sidebar.button('Check Database Status', key="check_db_status"):
        user_data = get_database_status()
        st.write("## Database Status")
        for user_id, addresses in user_data.items():
            st.write(f"User ID: {user_id}")
            for address in addresses:
                st.write(f"--- Address: {address}")

    # Update All Databases
    if st.sidebar.button('Update All Databases', key="update_all_dbs"):
        try:
            update_all_databases()
            st.success("All databases updated successfully.")
        except Exception as e:
            st.error(f"Error updating databases: {e}")

    # Save Raw Data for User to DB
    if st.sidebar.button('Save Raw Data to DB'):
        if selected_user_id:
            try:
                save_raw_data_for_user_to_db(selected_user_id)
                st.success(f"Data for User ID {selected_user_id} saved to database.")
            except Exception as e:
                st.error(f"Error saving data for User ID {selected_user_id} to database: {e}")
        else:
            st.warning("Please select a User ID.")

    # Load Data from File and Save to DB
    if st.sidebar.button('Load Data from File and Save to DB', key="load_data_from_file"):
        if selected_user_id:
            try:
                load_data_from_file_and_save_to_db(selected_user_id)
                st.success(f"Data for User ID {selected_user_id} loaded from file and saved to database.")
            except Exception as e:
                st.error(f"Error loading data for User ID {selected_user_id} from file and saving to database: {e}")
        else:
            st.warning("Please select a User ID.")

    # Cleanup JSON File
    if st.sidebar.button('Cleanup JSON File', key="cleanup_json_file"):
        if selected_user_id:
            try:
                cleanup_json_file(selected_user_id)
                st.success(f"JSON file for User ID {selected_user_id} cleaned up.")
            except Exception as e:
                st.error(f"Error cleaning up JSON file for User ID {selected_user_id}: {e}")
        else:
            st.warning("Please select a User ID.")

if __name__ == "__main__":
    handle_db_management()
