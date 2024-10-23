import plotly.express as px
import streamlit as st
import pandas as pd
import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from urllib.parse import quote_plus
import altair as alt
import plotly.express as px
from datetime import datetime
from datetime import date
from PIL import Image
import psycopg2
import plotly.express as px
import matplotlib.pyplot as plt
from streamlit_dynamic_filters import DynamicFilters

# Function to get summary of the data
def get_summary(df):
    summary = {
        'Total Resources': df['arn'].nunique(),
        'Unique Resource Types': df['_cq_table'].nunique(),
        'Latest Sync Time': df['_cq_sync_time'].max(),
        'Top 5 Resource Types': df['_cq_table'].value_counts().head().to_dict()
    }
    return summary  

#Put your logo here:
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


connection_string = f'postgresql+psycopg2://postgres:8yPhb9N2ujAw6wQZT95E@recuperer.cluster-cr0s6i646p8u.us-east-1.rds.amazonaws.com:5432/recupererdb'
engine = create_engine(connection_string)

infra_query = "SELECT * FROM aws_resources WHERE _cq_sync_time = (SELECT MAX(_cq_sync_time) FROM aws_resources) AND _cq_table LIKE 'aws_ec2_%%' and account_id not like 'aws%%' and region not like 'unavai%%'" 
backup_query = "SELECT * FROM aws_resource_backup_status"

df = pd.read_sql(infra_query, engine)
backup_df = pd.read_sql(backup_query, engine)
dynamic_filters = DynamicFilters(df=backup_df, filters=['region', 'account_id', 'arn', '_cq_table'])




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

# Sidebar
with st.sidebar:
    st.markdown(f'''
        <style>
        section[data-testid="stSidebar"] {{
                width: 500px;
                background-color: #000b1a;
                }}
        section[data-testid="stSidebar"] h1 {{
                color: #e3eefc;
                }}
        section[data-testid="stSidebar"] p {{
                color: #ddd;
                text-align: left;
                }}
        section[data-testid="stSidebar"] svg {{
                fill: #ddd;
                }}
        </style>
    ''',unsafe_allow_html=True)
    st.title(":anchor: Recuperer")
    st.markdown("Recovery Resilience Simplified.")

    # aws_regions = df['region'].unique()
    # region_selected = st.selectbox('AWS Region',['All'] + list(aws_regions),label_visibility="visible")

    # aws_accounts = df['account_id'].unique()
    # account_selected = st.selectbox('AWS Account',['All'] + list(aws_accounts),label_visibility="visible")    

    # st.toast('Selected')

    # rt_list = list(df['_cq_table'].unique())   
    # # Allow user to select a specific resource type
    # selected_type = st.selectbox('Resource Type', ['All'] + rt_list,label_visibility="visible")

    # if region_selected != 'All':
    #     filtered_df = df[df['region'] == selected_type]
    # else:
    #     filtered_df = df    

    # if account_selected != 'All':
    #     filtered_df = df[df['account_id'] == selected_type]
    # else:
    #     filtered_df = df    

    # if selected_type != 'All':
    #     filtered_df = df[df['_cq_table'] == selected_type]
    # else:
    #     filtered_df = df                    

    # Customizing the select box
    st.markdown(f'''
    <style>
        .stSelectbox div div {{
                background-color: #fafafa;
                color: #333;
        }}
        .stSelectbox div div:hover {{
                cursor: pointer
        }}
        .stSelectbox div div .option {{
                background-color: red;
                color: #111;
        }}
        .stSelectbox div div svg {{
                fill: black;
        }}
    </style>
    ''', unsafe_allow_html=True)

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
    total_regions = len(df['region'].unique())

    # Calculate the total number of regions
    total_accounts = len(df['account_id'].unique())

    total_resource_tyes = len(df['_cq_table'].unique())

    total_resources = len(df['arn'].unique())

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
                <p>Total Resource(s)<br><span> %d </span></p>
            </div>            
        </div>
        """ % (total_regions, total_accounts, total_resource_tyes,total_resources),
        unsafe_allow_html=True
    )
    
    
# with midRow:

#     # Display summary
#     st.header('Summary')
#     st.write(backup_df)


with chartRow:

    dynamic_filters.display_filters(location='sidebar')
    dynamic_filters.display_df()

#     # Display sample data
#     st.subheader(f'Sample Data for {selected_type} Resource(s)')
#     st.dataframe(filtered_df.head())

#     # Additional visualizations based on the selected resource type
#     if selected_type != 'All':
#         st.subheader(f'Visualizations for {selected_type}')
        
#         # Example: Bar chart of resources by region
#         region_counts = filtered_df['region'].value_counts()
#         fig = px.bar(x=region_counts.index, y=region_counts.values, 
#                         labels={'x': 'Region', 'y': 'Count'})
#         st.plotly_chart(fig)


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
    
  
