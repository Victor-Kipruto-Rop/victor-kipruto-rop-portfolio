import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
import os

st.set_page_config(page_title="Equity Group: Pan-Africa Analytics", layout="wide", page_icon="🏦")

def load_data(query, snapshot_name):
    try:
        host = "postgres-equity" if os.path.exists("/.dockerenv") else "localhost"
        engine = create_engine(f'postgresql://equity_admin:equity_password@{host}:5441/equity_warehouse')
        return pd.read_sql(query, engine)
    except Exception:
        snapshot_path = f"dashboards/snapshots/{snapshot_name}.csv"
        if os.path.exists(snapshot_path):
            return pd.read_csv(snapshot_path)
        return pd.DataFrame()

st.title("🏦 Equity Group: Pan-Africa Financial Hub")
st.markdown("Consolidated performance monitoring across 7 markets.")

perf_df = load_data("SELECT * FROM mart_subsidiary_performance ORDER BY year", "mart_subsidiary_performance")

if not perf_df.empty:
    latest_year = perf_df['year'].max()
    latest_data = perf_df[perf_df['year'] == latest_year]
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Group Assets (B KES)", f"{latest_data['total_assets_m_kes'].sum()/1000:,.1f}B")
    col2.metric("Group Profit (B KES)", f"{latest_data['profit_after_tax_m_kes'].sum()/1000:,.1f}B")
    col3.metric("Digital Adoption", f"{latest_data['digital_txn_percentage'].mean():,.1f}%")
    col4.metric("Regional Markets", latest_data['subsidiary'].nunique())

    st.markdown("---")
    
    tab1, tab2 = st.tabs(["Regional Contribution", "Growth Trends"])
    
    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Asset Distribution by Market")
            fig_pie = px.pie(latest_data, names='subsidiary', values='total_assets_m_kes', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
        with c2:
            st.subheader("Profitability by Market")
            fig_bar = px.bar(latest_data.sort_values('profit_after_tax_m_kes'), x='subsidiary', y='profit_after_tax_m_kes', color='profit_after_tax_m_kes')
            st.plotly_chart(fig_bar, use_container_width=True)
            
    with tab2:
        st.subheader("Regional Profit Growth (Time Series)")
        fig_line = px.line(perf_df, x='year', y='profit_after_tax_m_kes', color='subsidiary', markers=True)
        st.plotly_chart(fig_line, use_container_width=True)

else:
    st.warning("Data not found. Ingesting mock data...")
    from Pan_Africa_Financial_Platform.ingestion.generate_subsidiary_data import generate_equity_financials
    generate_equity_financials()
    st.rerun()
