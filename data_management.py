import streamlit as st
import json

data_store = {}

def store_data(data=None):
    if data is not None:
        data_store['stored_data'] = data
    else:
        return data_store.get('stored_data', None)

def save_data_to_file(data):
    with open('data.json', 'w') as f:
        json.dump(data, f)

def load_data_from_file():
    with open('data.json', 'r') as f:
        data = json.load(f)
    return data
