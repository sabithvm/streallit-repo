import os
import time
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


LINEAGE_QUERY = "SELECT account_id, region,  backup_vault_name, recovery_point_arn, resource_arn,completion_date, created_by, creation_date, encryption_key_arn, iam_role_arn, last_restore_time, lifecycle, calculated_lifecycle,parent_recovery_point_arn, resource_name, resource_type, source_backup_vault_arn, status, status_message, vault_type,tags, backup_vault_arn,_cq_source_name,_cq_table FROM aws_backup_vault_recovery_points_lineage"

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
                  for key, value in row.items() if key != 'index' and not key.startswith('_cq')}
    
    # Create the root object with a unique ID and embed the camel_dict
    root_object = {
        "id": str(uuid4()),  # Generate a unique ID
        "data": camel_dict
    }
    
    return json.dumps(root_object, default=str)

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
        table_name = st.session_state.table_name
        try:
            resource_details_query = f"SELECT * FROM {table_name} t WHERE arn = '{resource_arn}' AND t._cq_sync_time = (SELECT MAX(_cq_sync_time) FROM {table_name})"
            #st.write('Executing Query ' + resource_details_query)
            response = requests.get(QUERY_API_ENDPOINT, params={'query': resource_details_query})
            if response.status_code == 200:
                result = response.json()
                data = json.loads(result['data'])
                lineage_df = pd.json_normalize(data)
                with st.status("Extracting resource meta data...", expanded=True) as status:
                    time.sleep(2)
                    status.update(label="Resource metadata extracted!", state="complete", expanded=False)
                    time.sleep(2)                  
                row_json=row_to_json_with_id(lineage_df)
                st.json(row_json,expanded=2) 
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")                

        # Create a button to call the API
        if st.button('Migrate', key='api_button'):            
            try:
                with st.status("Migrating resource...", expanded=True) as status:
                    st.write("Copying associated Recoverypoint.")
                    time.sleep(2)
                    st.write("Enhancing metadata information")
                    time.sleep(1)
                    st.write("Provisioning resource")
                    time.sleep(1)     
                    status.update(label="Resource Migrated!", state="complete", expanded=False)      
                st.balloons()
                st.write(resource_arn + ' migrated successfully')
            except requests.RequestException as e:
                st.error(f"An error occurred while calling the API: {str(e)}")

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
    
