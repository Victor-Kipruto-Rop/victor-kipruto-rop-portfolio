import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import os

st.set_page_config(page_title="KRA: Customs & Trade Analytics", layout="wide", page_icon="🚢")

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

st.title("🚢 KRA: Customs & Trade Intelligence")
st.markdown("Import/Export volume tracking, duty collection analysis, and risk profiling.")

# Load from Mart
mart_data = load_data("SELECT * FROM mart_duty_collection ORDER BY year DESC, total_value_m_kes DESC", "mart_duty_collection")

if not mart_data.empty:
    latest_year = mart_data['year'].max()
    latest_data = mart_data[mart_data['year'] == latest_year]
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Declared Value (B KES)", f"{latest_data['total_value_m_kes'].sum()/1000:,.1f}B")
    col2.metric("Total Duty (B KES)", f"{latest_data['total_duty_m_kes'].sum()/1000:,.2f}B")
    col3.metric("Avg Risk Score", f"{latest_data['avg_risk_score'].mean():,.1f}")
    col4.metric("Trading Partners", latest_data['origin_country'].nunique())

    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["Trade Flow", "Revenue Analytics", "Risk Management"])
    
    with tab1:
        st.subheader(f"Import Composition by Category ({latest_year})")
        fig_cat = px.pie(latest_data, names='commodity_category', values='total_value_m_kes', hole=0.4)
        st.plotly_chart(fig_cat, use_container_width=True)
        
        st.subheader("Top 10 Origin Countries by Value")
        country_vol = latest_data.groupby('origin_country')['total_value_m_kes'].sum().reset_index()
        fig_country = px.bar(country_vol.nlargest(10, 'total_value_m_kes'), x='origin_country', y='total_value_m_kes', color='total_value_m_kes')
        st.plotly_chart(fig_country, use_container_width=True)

    with tab2:
        st.subheader("Duty Efficiency (Duty vs Value)")
        fig_scatter = px.scatter(latest_data, x='total_value_m_kes', y='total_duty_m_kes', color='commodity_category', 
                                 size='total_volume_tons', hover_name='commodity_description', log_x=True, log_y=True)
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        st.subheader("Annual Duty Collection Trend")
        annual_duty = mart_data.groupby('year')['total_duty_m_kes'].sum().reset_index()
        fig_trend = px.area(annual_duty, x='year', y='total_duty_m_kes', markers=True)
        st.plotly_chart(fig_trend, use_container_width=True)

    with tab3:
        st.subheader("Customs Risk Profiling (Heatmap)")
        risk_matrix = latest_data.groupby(['origin_country', 'commodity_category'])['avg_risk_score'].mean().unstack()
        fig_risk = px.imshow(risk_matrix, color_continuous_scale='Reds')
        st.plotly_chart(fig_risk, use_container_width=True)
        
        st.subheader("High Risk Commodities (>70 Score)")
        high_risk = latest_data[latest_data['avg_risk_score'] > 70]
        st.table(high_risk[['origin_country', 'commodity_description', 'avg_risk_score', 'total_value_m_kes']])

else:
    st.warning("No data found. Ensure the ETL pipeline has run successfully.")
