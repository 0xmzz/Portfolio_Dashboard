# schema_tests.py
from api_calls import check_schema
import unittest
import pandas as pd
import json

class TestSchema(unittest.TestCase):
    def test_check_schema(self):
        # Load the expected schema from the config file
        with open('../config/schema_config.json', 'r') as f:
            expected_schema = json.load(f)

        # Create a mock DataFrame
        df = pd.DataFrame({
            'Chain Name': ['Ethereum'],
            'USD Value': [2000]
        })

        # Test the schema check function
        self.assertTrue(check_schema(df, expected_schema['chain_data']))
