import streamlit as st

from utils import to_decimal
from database import (initialize_db, load_all_user_ids, load_addresses_from_id,save_raw_data_for_user_to_file, save_raw_data_for_user_to_db, load_data_from_file_and_save_to_db, cleanup_json_file, fetch_total_balance, fetch_all_token_list, 
                      save_addresses_to_id, store_total_balance_data, 
                      store_all_token_list_data, drop_all_token_list_data_table, delete_address_for_user, 
                      create_user_id, delete_user_id, add_address_for_user, fetch_addresses_for_user, update_all_databases, load_data_from_file, fetch_user_ids)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json
import datetime
import pandas as pd
import os
from utils import to_decimal
from decimal import Decimal
from dotenv import load_dotenv
from user_id_management import handle_user_id_management
from data_loading import handle_data_loading
from db_management import handle_db_management

# rest of the main.py code...


# Load .env variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# SQLAlchemy setup
engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)

current_dir = os.path.dirname(__file__)
config_path = os.path.join(current_dir, 'config', 'schema_config.json')


current_dir = os.path.dirname(__file__)
config_path = os.path.join(current_dir, 'config', 'schema_config.json')

# Load the expected schema from the config file
with open(config_path, 'r') as f:
    expected_schema = json.load(f)

def store_all_token_list_data(user_id, address, token_data_df):
    session = Session()
    try:
        token_data_df.to_sql('all_token_list_data', engine, if_exists='replace', index=False)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error in store_all_token_list_data: {e}")
    finally:
        session.close()

# Streamlit UI
def main():
    st.title('Database Loader')
        # Add a button to initialize the database
    if st.sidebar.button('Initialize Database'):
            initialize_db()
            with open('last_init_time.txt', 'w') as f:
                f.write(str(datetime.datetime.now()))
            st.sidebar.success('Database initialized.')

        # Display the last time the database was initialized
    try:
            with open('last_init_time.txt', 'r') as f:
                last_init_time = f.read()
            st.sidebar.write(f"Last initialized: {last_init_time}")
    except FileNotFoundError:
            st.sidebar.write("Database not initialized yet.")

    # Create a tab-like interface using st.radio
    tab_selection = st.radio("Choose a tab:", ["User ID Management", "API Data Loading and Fetching from file", "Database Management"])
        
    if tab_selection == "User ID Management":
        handle_user_id_management()
       

    if tab_selection == "API Data Loading and Fetching from file":
       handle_data_loading()
        

    if tab_selection == "Database Management":
        handle_database_management()

if __name__ == '__main__':
    main()



    