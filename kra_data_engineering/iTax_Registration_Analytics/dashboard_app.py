import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import os

st.set_page_config(page_title="KRA: iTax Business Analytics", layout="wide", page_icon="🏢")

def load_data(query, snapshot_name):
    try:
        if os.path.exists("/.dockerenv"):
            host = "postgres-kra"
            port = "5432"
        else:
            host = "localhost"
            port = "5438"
            
        engine = create_engine(f'postgresql://kra_admin:kra_password@{host}:{port}/kra_warehouse')
        return pd.read_sql(query, engine)
    except Exception as e:
        st.sidebar.warning(f"Live DB connection failed: {e}. Using snapshots.")
        snapshot_path = f"dashboards/snapshots/{snapshot_name}.csv"
        if os.path.exists(snapshot_path):
            return pd.read_csv(snapshot_path)
        return pd.DataFrame()

st.title("🏢 KRA: iTax Business Registration Analytics")
st.markdown("Tracking new business formation rates and taxpayer density by county and sector.")

df = load_data("SELECT * FROM mart_registrations_summary", "mart_registrations_summary")

if not df.empty:
    df['registration_month'] = pd.to_datetime(df['registration_month'])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Recorded Periods", len(df))
    col2.metric("Total New Registrations", df['new_registrations'].sum())
    col3.metric("Top County", df.groupby('county')['new_registrations'].sum().idxmax())

    st.markdown("---")
    
    tab1, tab2 = st.tabs(["Registration Trends", "Geospatial Density"])
    
    with tab1:
        st.subheader("Monthly Registration Volume")
        df_monthly = df.groupby('registration_month')['new_registrations'].sum().reset_index()
        fig_trend = px.area(df_monthly, x='registration_month', y='new_registrations', title="Business Formation Rate")
        st.plotly_chart(fig_trend, use_container_width=True)
        
    with tab2:
        st.subheader("Taxpayer Concentration by County & Sector")
        fig_county = px.treemap(df, path=['county', 'sector'], values='new_registrations', title="Business Density Map")
        st.plotly_chart(fig_county, use_container_width=True)

else:
    st.warning("No data found. Ensure the ETL pipeline has run successfully.")
