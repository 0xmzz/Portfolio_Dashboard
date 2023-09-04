# Import necessary modules
import streamlit as st
from datahouse.api_calls import fetch_aggregated_data, fetch_total_balance, fetch_user_relevant_protocols, fetch_user_protocol_data
from datahouse.data_processing import process_balance_data, process_protocol_data
from database import save_raw_data_to_db, get_all_portfolio_data, store_portfolio_data, get_latest_portfolio_data, load_raw_data_from_db
from datahouse.address_management import manage_addresses
import pandas as pd
import plotly.express as px
from datahouse.data_standardization import standardize_and_flatten_protocol_data, standardize_chain_data


# Function to display the total USD value of the portfolio
def display_total_usd_value(df):
    total_usd = df['USD Value'].sum()
    st.write(f"**Total Portfolio Value:** ${total_usd:,.2f}")
  
def aggregate_data(chain_data, protocol_data):
    if not protocol_data.empty:
        # Renaming columns to match the expected names
        protocol_data = protocol_data.rename(columns={
            'Chain': 'Chain Name',
            'Token Amount': 'Amount'
        })
        
        missing_columns = [col for col in ['Chain Name', 'Protocol Name', 'Amount', 'USD Value'] if col not in protocol_data.columns]
        if missing_columns:
            print(f"Missing columns in protocol_data: {missing_columns}")
        else:
            protocol_data = protocol_data[['Chain Name', 'Protocol Name', 'Amount', 'USD Value']]
            
    combined_df = pd.concat([chain_data, protocol_data], ignore_index=True)
    return combined_df


def display_portfolio_trend(user_id):
    all_data = get_all_portfolio_data(user_id)
    if all_data:
        timestamps, chain_data_list, protocol_data_list = zip(*all_data)
        usd_values = [pd.read_json(cd)['USD Value'].sum() for cd in chain_data_list]
        trend_df = pd.DataFrame({'Timestamp': timestamps, 'USD Value': usd_values})
        fig = px.line(trend_df, x='Timestamp', y='USD Value', title='Portfolio Trend Over Time')
        st.plotly_chart(fig, use_container_width=True)

def main():
    st.title("DeBank Portfolio Dashboard")
    user_id = "user_id_placeholder"
    addresses = manage_addresses(key_suffix="unique_suffix_1")

    for i, address in enumerate(addresses):
        api_call_selection = st.selectbox(f"Select API Call for {address}", ["Get Balance", "Get NFT List"], key=f'api_call_selection_key_{i}')

    df = None


    if st.button("Update Database from API"):
        print("Button pressed, calling API functions...")
        chain_data = []
        protocol_data = []

        for address in addresses:
            chain_balance_data = fetch_total_balance(address)
            if chain_balance_data:
                chain_data.append(process_balance_data(chain_balance_data))

        if api_call_selection == "Get Balance":
            print("Entered 'Get Balance' block.")
            for address in addresses:
                relevant_protocols = fetch_user_relevant_protocols(address)
                print(f"Relevant protocols for address {address}: {relevant_protocols}")

                for protocol_id in relevant_protocols:
                    print(f"Fetching protocol data for from main.py protocol_id {protocol_id} and address {address}")
                    user_protocol_data = fetch_user_protocol_data(protocol_id, address)

                    try:
                        # Convert the dictionary to a DataFrame
                        print(f"Converting JSON to DataFrame: {user_protocol_data}")
                        user_protocol_data_df = pd.json_normalize(user_protocol_data, sep='_')
                        
                        # Standardize the DataFrame before passing it to process_protocol_data
                        print(f"DataFrame before passing to standardize_and_flatten_protocol_data: {user_protocol_data_df}")
                        user_protocol_data_df = standardize_and_flatten_protocol_data(user_protocol_data_df)  
                        
                        print(f"DataFrame before passing to process_protocol_data, normalized: {user_protocol_data_df}")

                        if not user_protocol_data_df.empty:
                            processed_protocol_data, _ = process_protocol_data(user_protocol_data_df)  # Unpack tuple here
                            protocol_data.append(processed_protocol_data)
                            
                    except Exception as e:
                        print(f"Error converting JSON to DataFrame: {e}")

        # Make sure all items in protocol_data are DataFrames
        protocol_data = [df for df in protocol_data if isinstance(df, pd.DataFrame)]

        # Now concatenate
        chain_data_df = pd.concat(chain_data, ignore_index=True) if chain_data else pd.DataFrame()
        protocol_data_df = pd.concat(protocol_data, ignore_index=True) if protocol_data else pd.DataFrame()


        chain_data_json = [x.to_json() if isinstance(x, pd.DataFrame) else x for x in chain_data] #converts each DataFrame in chain_data to a JSON string. If an element in chain_data is not a DataFrame, it leaves it as is.
        
        protocol_data_json = [x.to_json() if isinstance(x, pd.DataFrame) else x for x in protocol_data] #converts each DataFrame in protocol_data to a JSON string. If an element in protocol_data is not a DataFrame, it leaves it as is.

        save_raw_data_to_db(user_id, {'chain_data': chain_data_json, 'protocol_data': protocol_data_json}) # Save the raw data to the database
        store_portfolio_data(user_id, chain_data_df, protocol_data_df) # Store the processed data to the database
        
  
    if st.button("Refresh from Database"):
        raw_data = load_raw_data_from_db("user_id_placeholder")
        st.write(f"Loaded from DB: {raw_data}")
        if raw_data is not None:
            chain_data = [pd.read_json(x) if x else pd.DataFrame() for x in raw_data.get('chain_data', [])]
            protocol_data_list = [pd.read_json(x) if x else pd.DataFrame() for x in raw_data.get('protocol_data', [])]

            if chain_data is not None:
                chain_data = pd.concat(chain_data, ignore_index=True)

            processed_protocol_data_list = []
            if protocol_data_list is not None:
                for protocol_data in protocol_data_list:
                    # Unpack the tuple here
                    processed_protocol_data, _ = process_protocol_data(protocol_data)
                    processed_protocol_data_list.append(processed_protocol_data)

                protocol_data = pd.concat(processed_protocol_data_list, ignore_index=True)
                print("Processed protocol data:", protocol_data)

        df = aggregate_data(chain_data, protocol_data)

        st.write("### Chain Data")
        st.write(chain_data)

        st.write("### Protocol Data")
        st.write(protocol_data)

        st.write(df)

        if df is not None:
            total_usd = df['USD Value'].sum()
            st.write(f"**Total Portfolio Value:** ${total_usd:,.2f}")

    if df is not None and not df.empty:
        fig = px.pie(df, values='USD Value', names='Chain Name', title='Portfolio Distribution by Chain')
        st.plotly_chart(fig, use_container_width=True)

    if st.button("Show Portfolio Trend"):
        display_portfolio_trend(user_id)

if __name__ == "__main__":
    main()