import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime

# Function to fetch data from the API
def fetch_data():
    url = "https://api.neso.energy/api/3/action/datastore_search"
    params = {
        "resource_id": "17becbab-e3e8-473f-b303-3806f43a6a10",  # Replace with the correct resource ID
        "limit": 1000  # Adjust as needed
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()['result']['records']
    else:
        st.error(f"Failed to fetch data: {response.status_code}")
        return None

# Function to process the data
def process_data(data):
    df = pd.DataFrame(data)
    return df

# Streamlit app
def main():
    st.title("Total Power Generation Trend")

    # Fetch data
    data = fetch_data()
    if data:
        # Process data
        df = process_data(data)

        # Create line chart
        st.dataframe(df)

    else:
        st.write("No data available.")

if __name__ == "__main__":
    main()
