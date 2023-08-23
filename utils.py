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
