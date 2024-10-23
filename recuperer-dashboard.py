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


connection_string = f'postgresql+psycopg2://postgres:8yPhb9N2ujAw6wQZT95E@recuperer.cluster-cr0s6i646p8u.us-east-1.rds.amazonaws.com:5432/recupererdb'
engine = create_engine(connection_string)

query = "SELECT * FROM aws_resources WHERE _cq_sync_time = (SELECT MAX(_cq_sync_time) FROM aws_resources) AND _cq_table LIKE 'aws_ec2_%%'" 

df = pd.read_sql(query, engine)

#######################
# Page configuration
st.set_page_config(
    page_title="Recuperer Dashboard",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")

#######################
# CSS styling
st.markdown("""
<style>

[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}

[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

[data-testid="stMetric"] {
    background-color: #393939;
    text-align: center;
    padding: 15px 0;
}

[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
}

[data-testid="stMetricDeltaIcon-Up"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

</style>
""", unsafe_allow_html=True)






# Function to get summary of the data
def get_summary(df):
    summary = {
        'Total Resources': len(df),
        'Unique Resource Types': df['_cq_table'].nunique(),
        'Latest Sync Time': df['_cq_sync_time'].max(),
        'Top 5 Resource Types': df['_cq_table'].value_counts().head().to_dict()
    }
    return summary

# Streamlit app
def main():
    st.title('Recuperer Dashboard')

    try:
        
        #Put your logo here:
        logo = Image.open('resources/logo.jpg')
        logo = logo.resize((200, 100))#and make it to whatever size you want.


        #######################
        # Sidebar
        with st.sidebar:
            st.title('🏂 Recuperer Dashboard')
            
            rt_list = list(df['_cq_table'].unique())            
            selected_rt = st.selectbox('Select a Resource Type', rt_list)

        # Get summary
        summary = get_summary(df)

        # Display summary
        st.header('Summary')
        st.write(f"Total Resources: {summary['Total Resources']}")
        st.write(f"Unique Resource Types: {summary['Unique Resource Types']}")
        st.write(f"Latest Sync Time: {summary['Latest Sync Time']}")

        # Bar chart of top resource types
        st.subheader('Top Resource Types')
        top_resources = df['_cq_table'].value_counts().head(10)
        fig = px.bar(x=top_resources.index, y=top_resources.values, 
                     labels={'x': 'Resource Type', 'y': 'Count'})
        st.plotly_chart(fig)
        rt_list = list(df['_cq_table'].unique())   


        # Allow user to select a specific resource type
        selected_type = st.selectbox('Select a resource type', rt_list)

        if selected_type != 'All':
            filtered_df = df[df['_cq_table'] == selected_type]
        else:
            filtered_df = df

        # Display sample data
        st.subheader(f'Sample Data for {selected_type}')
        st.dataframe(filtered_df.head())

        # Additional visualizations based on the selected resource type
        if selected_type != 'All':
            st.subheader(f'Visualizations for {selected_type}')
            
            # Example: Bar chart of resources by region
            region_counts = filtered_df['region'].value_counts()
            fig = px.bar(x=region_counts.index, y=region_counts.values, 
                         labels={'x': 'Region', 'y': 'Count'})
            st.plotly_chart(fig)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
