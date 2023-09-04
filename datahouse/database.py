import sqlite3
import json
import pandas as pd

DB_FILE = 'debank_data.db'

def execute_query(query, params=()):
    try:
        conn = sqlite3.connect('your_database_file.db')
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Database error: {e}")


def execute_query_with_result(query, params=()):
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    except sqlite3.Error as e:
        raise Exception(f"Database error in execute_query_with_results: {e}")

# Moved these lines to the top-level indentation
def initialize_db():
    execute_query('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            addresses TEXT
        );
    ''')

    execute_query('''
    CREATE TABLE IF NOT EXISTS total_balance_data (
        user_id TEXT,
        address TEXT,
        timestamp DATETIME,
        chain_data TEXT
    );
    ''')

    execute_query('''
    CREATE TABLE IF NOT EXISTS all_token_list_data (
        user_id TEXT,
        address TEXT,
        timestamp DATETIME,
        token_data TEXT
    );
    ''')

def save_addresses_to_id(user_id, addresses):
    execute_query('INSERT OR REPLACE INTO users (user_id, addresses) VALUES (?, ?)', (user_id, json.dumps(addresses)))

def load_addresses_from_id(user_id):
    result = execute_query_with_result('SELECT addresses FROM users WHERE user_id = ?', (user_id,))
    return json.loads(result[0][0]) if result else []

def store_total_balance_data(user_id, address, chain_data_df):
    with sqlite3.connect(DB_FILE) as conn:
        chain_data_df.to_sql('total_balance_data', conn, if_exists='replace', index=False)
        # Add code to associate this data with user_id and address

def store_all_token_list_data(user_id, address, token_data_df):
    try:
        print("Before conversion:", token_data_df.dtypes)
        
        for col in token_data_df.columns:
            token_data_df[col] = token_data_df[col].astype(str)
        
        print("After conversion:", token_data_df.dtypes)
        
        with sqlite3.connect(DB_FILE) as conn:
            token_data_df['user_id'] = user_id
            token_data_df['address'] = address
            token_data_df.to_sql('all_token_list_data', conn, if_exists='append', index=False)
            conn.commit()
            
        print("Data stored successfully.")
        
    except Exception as e:
        print(f"An error occurred: {e}")



def load_all_user_ids():
    return [row[0] for row in execute_query_with_result("SELECT user_id FROM users")]

def load_saved_data(user_id, address):
    saved_balance_data = execute_query_with_result('SELECT chain_data FROM total_balance_data WHERE user_id = ? AND address = ?', (user_id, address))
    saved_token_data = execute_query_with_result('SELECT token_data FROM all_token_list_data WHERE user_id = ? AND address = ?', (user_id, address))

    # Convert JSON string to DataFrame
    saved_balance_data = pd.read_json(saved_balance_data[0][0]) if saved_balance_data is not None else None
    saved_token_data = pd.read_json(saved_token_data[0][0]) if saved_token_data is not None else None

    return saved_balance_data, saved_token_data


if __name__ == "__main__":
    # No need to call initialize_db() as the tables are created at the top level
    pass
