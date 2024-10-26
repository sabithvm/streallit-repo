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

logo = Image.open(LOGO_PATH)
logo = logo.resize(LOGO_SIZE)

BACKUP_QUERY = "SELECT * FROM aws_resource_backup_status"
LINEAGE_QUERY = "SELECT * FROM aws_backup_vault_recovery_points_lineage"

# Get the API endpoint from environment variable
QUERY_API_ENDPOINT = os.environ.get('QUERY_API_ENDPOINT')
QUERY_API_ENDPOINT = 'https://kxdb7ecp8f.execute-api.us-east-1.amazonaws.com/prod/query'

EXEC_API_ENDPOINT = os.environ.get('EXEC_API_ENDPOINT')
EXEC_API_ENDPOINT = 'https://kxdb7ecp8f.execute-api.us-east-1.amazonaws.com/prod/execute'

if not QUERY_API_ENDPOINT:
    st.error("QUERY_API_ENDPOINT environment variable is not set.")
    st.stop()

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


backup_df = pd.DataFrame()
if BACKUP_QUERY:
    try:
        response = requests.get(QUERY_API_ENDPOINT, params={'query': BACKUP_QUERY})
        if response.status_code == 200:
            result = response.json()
            data = json.loads(result['data'])
            backup_df = pd.json_normalize(data)
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

alt.themes.enable("dark")

# CSS styles
# Custom styling for top and down
st.markdown(
    """
    <style>
    .top-stats {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin: 12px 0 40px 0;
        width: 100%;
        height: 40px;
        text-align: center;
    }
    .subheader {
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .stat {
        flex: 1; 
        font-weight: bold;
        border-radius: 4px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        background-color: #111;

        display: flex;
        justify-content: center;
        align-items: center;
        text-align: center;
    }
    .stat p {
        padding-top: 8px;
    }
    .stat p {
        color: #bbb;
        font-size: 12px;
    }
    .stat span {
        color: #ddd;
        font-size: 24px;
        font-family: serif;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# The Hero Section
with hero:
    # the logo
    st.markdown("""<div style="position:relative; margin: auto; text-align: center;">
              <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Map-circle-blue.svg/1024px-Map-circle-blue.svg.png" width=56>
            </div>""", unsafe_allow_html=True)

    # the header
    st.markdown('<h1 style="text-align:center; position:relative; top:40%;">Recuperer</h1>', unsafe_allow_html=True)


# The Rows
with topRow:

    # Calculate the total number of regions
    total_regions = len(backup_df['region'].unique())

    # Calculate the total number of regions
    total_accounts = len(backup_df['account_id'].unique())

    total_resource_tyes = len(backup_df['_cq_table'].unique())

    total_rps = len(backup_df['arn'].unique())

    # the result is 2:14 PM so I'll type it by hand for now.
    st.markdown(
        """
        <div class="subheader">Inventory Summary</div>
        <div class="top-stats">
            <div class="stat">
                <p>Total Region(s)<br><span> %d </span></p>
            </div>
            <div class="stat">
                <p>Total Account(s)<br><span> %d </span></p>
            </div>
            <div class="stat">
                <p>Total Resource Type(s)<br><span> %d </span></p>
            </div>
            <div class="stat">
                <p>Total Recoverypoint(s)<br><span> %d </span></p>
            </div>            
        </div>
        """ % (total_regions, total_accounts, total_resource_tyes,total_rps),
        unsafe_allow_html=True
    )
    
    
with midRow:

    st.header("Data Protection Coverage")    
    gb = GridOptionsBuilder.from_dataframe(backup_df)
    gb.configure_selection('single', use_checkbox=True, pre_selected_rows=[])
    gb.configure_column("arn", editable=False)
    gb.configure_default_column(resizable=True, filterable=True, sorteable=True)
    grid_options = gb.build()

    grid_response = AgGrid(
        backup_df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
        fit_columns_on_grid_load=True,
        allow_unsafe_jscode=True,
        theme='streamlit'
    )
    if not(grid_response['selected_rows'] is None):
        if len(grid_response['selected_rows'])>0:
            selected_row = grid_response['selected_rows'][0]
            resource_arn = selected_row['arn']
            st.session_state.resource_arn = resource_arn
            st.switch_page("pages/recuperer-lineage.py")         
    else:
        st.warning("Please select a row before calling the API.")        


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
    
