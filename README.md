# DeBank Portfolio Dashboard

A Streamlit application to fetch and display portfolio data from DeBank's API.

## Setup

Clone the repository:

git clone https://github.com/0xmzz/your-repo-name.git

Create a .env file in the root directory and add your DeBank API key:

DEBANK_API_KEY=your_api_key_here

to run the app:
streamlit run main.py

Project Summary:
Building a PoC Streamlit application that interfaces with the DeBank API to fetch and display portfolio data. The application allows users to input one or multiple Ethereum addresses, select the type of API call, and then either fetch fresh data from the API or pull previously fetched data from a cache. The fetched data is then displayed in a table format, and if the data is related to balances, it's also visualized in a pie chart. Additionally, there's an option to download the displayed data as a CSV file.

File Architecture:
config.py: Contains configurations like the DeBank API URL and headers.
Loads environment variables, including the DeBank API key.

data_processing.py: Contains functions to process raw data fetched from the API.
Functions like process_balance_data and process_nft_data are present here.

api_calls.py: Contains functions to make API calls.
Functions like fetch_total_balance and fetch_nft_list are present here.

utils.py: Contains utility functions like store_data, save_data_to_file, and load_data_from_file.
Handles caching and file storage/retrieval operations.

main.py: Contains the main Streamlit application.
Has the main function which drives the UI and the interactions.
Uses functions from the other modules to fetch, process, and display data.

.env: Stores environment variables, like the DeBank API key.

Current State & Issues:
The main function was recently modified to handle multiple Ethereum addresses.
An error occurred due to a variable scope issue, which was addressed by looping over each address in the address_list to fetch data for it.
The application now supports caching using Streamlit's session state and also offers file storage for persistence across restarts.
Next Steps: further modularize the application, improve error handling, and add more features.
There's potential to expand on the user management aspect, allowing users to save multiple addresses under a user ID for easier retrieval in the future.

This project is licensed under the MIT License.
