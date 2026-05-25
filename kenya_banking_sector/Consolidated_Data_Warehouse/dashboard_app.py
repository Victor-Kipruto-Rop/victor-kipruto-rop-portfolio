import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import os

st.set_page_config(page_title="Kenya Banking Sector: Consolidated DWH", layout="wide", page_icon="🏦")

def load_data(query, snapshot_name):
    try:
        host = "postgres" if os.path.exists("/.dockerenv") else "localhost"
        engine = create_engine(f'postgresql://sector_admin:sector_password@{host}:5437/sector_dwh')
        return pd.read_sql(query, engine)
    except Exception:
        # Fallback to snapshots if they exist
        snapshot_path = f"dashboards/snapshots/{snapshot_name}.csv"
        if os.path.exists(snapshot_path):
            return pd.read_csv(snapshot_path)
        return pd.DataFrame()

st.title("🏦 Kenya Banking Sector: Consolidated Analytics")
st.markdown("Aggregated financial data from all 38+ licensed banks (CBK Supervision Reports).")

kpis = load_data("SELECT * FROM mart_sector_kpis ORDER BY year DESC, total_assets DESC", "mart_sector_kpis")

if not kpis.empty:
    latest_year = kpis['year'].max()
    latest_data = kpis[kpis['year'] == latest_year]
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Sector Assets (B KES)", f"{latest_data['total_assets'].sum()/1000:,.0f}B")
    col2.metric("Total Sector Deposits (B KES)", f"{latest_data['total_deposits'].sum()/1000:,.0f}B")
    col3.metric("Avg Sector NPL %", f"{latest_data['npl_ratio'].mean():,.1f}%")
    col4.metric("Total Licensed Banks", latest_data['bank_id'].nunique())

    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["Market Share", "Asset Quality", "Peer Benchmarking"])
    
    with tab1:
        st.subheader(f"Market Share by Total Assets ({latest_year})")
        fig_share = px.pie(latest_data, names='bank_name', values='total_assets', hole=0.4, title="Asset Distribution")
        st.plotly_chart(fig_share, use_container_width=True)
        
        st.subheader("Top 10 Banks by Deposits")
        fig_dep = px.bar(latest_data.nlargest(10, 'total_deposits'), x='bank_name', y='total_deposits', color='tier')
        st.plotly_chart(fig_dep, use_container_width=True)

    with tab2:
        st.subheader("NPL Ratio vs. Total Assets")
        fig_npl = px.scatter(latest_data, x='total_assets', y='npl_ratio', size='net_loans', color='tier', 
                             hover_name='bank_name', log_x=True, title="Risk vs Scale")
        st.plotly_chart(fig_npl, use_container_width=True)
        
    with tab3:
        st.subheader("ROA vs Loan-to-Deposit Ratio")
        selected_banks = st.multiselect("Select Banks to Compare", kpis['bank_name'].unique(), default=["KCB Bank Kenya", "Equity Bank Kenya", "Absa Bank Kenya"])
        comparison_data = kpis[kpis['bank_name'].isin(selected_banks)]
        
        fig_comp = px.line(comparison_data, x='year', y='roa', color='bank_name', markers=True)
        st.plotly_chart(fig_comp, use_container_width=True)

else:
    st.warning("No data found. Please run the pipeline first.")
