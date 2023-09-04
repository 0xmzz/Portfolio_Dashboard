import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the API key from the environment variable
DEBANK_KEY = os.getenv("DEBANK_API_KEY")

DEBANK_API_URL = "https://pro-openapi.debank.com"

headers = {
    "accept": "application/json",
    "AccessKey": DEBANK_KEY,
}

def check_schema(df, expected_columns, default_value=0):
    missing_columns = set(expected_columns) - set(df.columns)
    extra_columns = set(df.columns) - set(expected_columns)
    
    schema_is_ok = True
    
    if missing_columns:
        for col in missing_columns:
            df[col] = default_value
        schema_is_ok = False

    if extra_columns:
        df.drop(columns=list(extra_columns), inplace=True)
        schema_is_ok = False
    
    return schema_is_ok





