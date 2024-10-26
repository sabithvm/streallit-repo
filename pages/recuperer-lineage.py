import os
from datetime import datetime, date
from urllib.parse import quote_plus

import altair as alt
import pandas as pd
import json
from uuid import uuid4
import plotly.express as px
import streamlit as st
from PIL import Image
from streamlit_dynamic_filters import DynamicFilters
import requests
from st_aggrid import AgGrid, GridUpdateMode
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid import AgGrid, GridUpdateMode, ColumnsAutoSizeMode

# Configuration and constants
PAGE_TITLE = "Recuperer Dashboard"
LOGO_PATH = 'resources/logo.jpg'
LOGO_SIZE = (200, 100)


LINEAGE_QUERY = "SELECT account_id, region,  backup_vault_name, recovery_point_arn, resource_arn,completion_date, created_by, creation_date, encryption_key_arn, iam_role_arn, last_restore_time, lifecycle, calculated_lifecycle,parent_recovery_point_arn, resource_name, resource_type, source_backup_vault_arn, status, status_message, vault_type,tags, backup_vault_arn FROM aws_backup_vault_recovery_points_lineage"

# Get the API endpoint from environment variable
QUERY_API_ENDPOINT = os.environ.get('QUERY_API_ENDPOINT')
QUERY_API_ENDPOINT = 'https://kxdb7ecp8f.execute-api.us-east-1.amazonaws.com/prod/query'

EXEC_API_ENDPOINT = os.environ.get('EXEC_API_ENDPOINT')
EXEC_API_ENDPOINT = 'https://kxdb7ecp8f.execute-api.us-east-1.amazonaws.com/prod/execute'

if not QUERY_API_ENDPOINT:
    st.error("QUERY_API_ENDPOINT environment variable is not set.")
    st.stop()
def camel_case(s):
    """Convert snake_case to camelCase."""
    parts = s.split('_')
    return ''.join(p.title() for p in parts)

def row_to_json_with_id(row):
    """Convert a DataFrame row to a JSON object with CamelCase keys, embedded in a root object with a unique ID."""
    camel_dict = {camel_case(key): value.iloc[0] if isinstance(value, pd.Series) else value 
                  for key, value in row.items() if key != 'index'}
    
    # Create the root object with a unique ID and embed the camel_dict
    root_object = {
        "id": str(uuid4()),  # Generate a unique ID
        "data": camel_dict
    }
    
    return json.dumps(root_object, default=str)

def display_lineage_data_frame(lineage_df):
    with chartRow:

        st.header("Recoverypoint Lineage")    
        gb = GridOptionsBuilder.from_dataframe(lineage_df)
        gb.configure_selection('single', use_checkbox=True, pre_selected_rows=[])
        gb.configure_default_column(resizable=True, filterable=True, sorteable=True)
        grid_options = gb.build()

        grid_response = AgGrid(
            lineage_df,
            gridOptions=grid_options,
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
            fit_columns_on_grid_load=True,
            allow_unsafe_jscode=True,
            theme='streamlit'
        )

        selected_row = grid_response['selected_rows']
        if not(selected_row is None):
            # Create a button to call the API
            if st.button('Migrate', key='api_button'):            
                try:
                    row_json=row_to_json_with_id(selected_row)
                    st.json(row_json,expanded=2)                    
                except requests.RequestException as e:
                    st.error(f"An error occurred while calling the API: {str(e)}")
        else:
            st.warning("Please select a row before calling the API.") 
            

logo = Image.open('resources/logo.jpg')
logo = logo.resize((200, 100))#and make it to whatever size you want.

# the layout Variables
st.set_page_config(page_title="Recuperer Dashboard", 
                   page_icon=logo,
                   layout="wide",
                   initial_sidebar_state="expanded",
                   )

hero = st.container()
topRow = st.container()
midRow = st.container()
chartRow = st.container()
footer = st.container()



    
with midRow:

    if 'resource_arn' in st.session_state:
        resource_arn = st.session_state.resource_arn
        try:
            if LINEAGE_QUERY:
                try:
                    lineage_query = LINEAGE_QUERY + " where resource_arn='"+ resource_arn +"'"
                    response = requests.get(QUERY_API_ENDPOINT, params={'query': lineage_query})
                    if response.status_code == 200:
                        result = response.json()
                        data = json.loads(result['data'])
                        lineage_df = pd.json_normalize(data)
                        display_lineage_data_frame(lineage_df)
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")                
        except requests.RequestException as e:
            st.error(f"An error occurred while calling the API: {str(e)}")
    else:
        st.warning("No row selected. Please go back to the home page and select a row.")
            


with footer:
    st.markdown("---")
    st.markdown(
        """
        <style>
            p {
                font-size: 16px;
                text-align: center;
            }
            a {
                text-decoration: none;
                color: #00a;
                font-weight: 600;
            }
        </style>
        <p>
            &copy; 2024 Recuperer, Inc.
        </p>
        """, unsafe_allow_html=True
        )
    
