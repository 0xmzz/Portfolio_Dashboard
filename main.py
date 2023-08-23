import streamlit as st
from api_calls import fetch_total_balance, fetch_nft_list
from data_processing import process_balance_data, process_nft_data
from data_management import store_data, save_data_to_file, load_data_from_file
import base64
import plotly.express as px

def main():
    st.title("DeBank Portfolio Dashboard")
    
    # Input for Ethereum addresses (multiple addresses separated by commas)
    addresses = st.text_input("Enter Ethereum Addresses (comma-separated):", "")
    address_list = [address.strip() for address in addresses.split(",")]
    
    # Dropdown for API call selection
    api_call_selection = st.selectbox("Select API Call", ["Get Balance", "Get NFT List"])
    
    # Buttons to refresh and get data from the API or pull from cache
    refresh_data = st.button("Refresh Data")
    pull_from_cache = st.button("Pull from Cache")
    
    if refresh_data:
        for address in address_list:
            if api_call_selection == "Get Balance":
                data = fetch_total_balance(address)
                if data:
                    df = process_balance_data(data)
            elif api_call_selection == "Get NFT List":
                data = fetch_nft_list(address)
                if data:
                    df = process_nft_data(data)
            
            if data:
                # Store the df in cache
                store_data(df)
                
                st.write(df)
                
                # Pie chart visualization for balance data
                if api_call_selection == "Get Balance":
                    fig = px.pie(df, values='USD Value', names='Chain Name', title='Portfolio Distribution by Chain')
                    st.plotly_chart(fig)
                
                # CSV download link
                csv = df.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()
                href = f'<a href="data:file/csv;base64,{b64}" download="data.csv">Download CSV File</a>'
                st.markdown(href, unsafe_allow_html=True)
            else:
                st.write(f"No data found for the provided address: {address}")
                
    elif pull_from_cache:
        # Retrieve the df from cache
        cached_data = store_data()
        if cached_data is not None:
            st.write(cached_data)
            
            # Pie chart visualization for balance data
            if api_call_selection == "Get Balance":
                fig = px.pie(cached_data, values='USD Value', names='Chain Name', title='Portfolio Distribution by Chain')
                st.plotly_chart(fig)
            
            # CSV download link
            csv = cached_data.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="data.csv">Download CSV File</a>'
            st.markdown(href, unsafe_allow_html=True)
        else:
            st.write("No cached data found. Please click 'Refresh Data' first.")

   
if __name__ == "__main__":
    main()
