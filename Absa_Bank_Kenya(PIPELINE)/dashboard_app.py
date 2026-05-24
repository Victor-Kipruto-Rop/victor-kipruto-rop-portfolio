import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
import os

st.set_page_config(page_title="Absa Kenya: Financial Analytics", layout="wide", page_icon="🔴")

def load_data(query, snapshot_name):
    try:
        host = "postgres-absa" if os.path.exists("/.dockerenv") else "localhost"
        engine = create_engine(f'postgresql://absa_admin:absa_password@{host}:5440/absa_warehouse')
        return pd.read_sql(query, engine)
    except Exception:
        snapshot_path = f"dashboards/snapshots/{snapshot_name}.csv"
        if os.path.exists(snapshot_path):
            return pd.read_csv(snapshot_path)
        return pd.DataFrame()

st.title("🔴 Absa Bank Kenya: Financial Insights")
st.markdown("Automated tracking of Tier 1 banking performance metrics.")

prof_df = load_data("SELECT * FROM mart_profitability ORDER BY year", "mart_profitability")
eff_df = load_data("SELECT * FROM mart_efficiency_ratio ORDER BY year", "mart_efficiency_ratio")

if not prof_df.empty:
    latest_year = prof_df['year'].max()
    latest_prof = prof_df[prof_df['year'] == latest_year]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Net Profit (M KES)", f"{latest_prof['net_profit'].iloc[0]:,.0f}")
    col2.metric("ROE %", f"{latest_prof['roe_percent'].iloc[0]:,.2f}%")
    
    if not eff_df.empty:
        latest_eff = eff_df[eff_df['year'] == latest_year]
        col3.metric("Cost-to-Income", f"{latest_eff['cost_to_income_ratio'].iloc[0]:,.1f}%")

    st.markdown("---")
    
    tab1, tab2 = st.tabs(["Profitability Trends", "Operational Efficiency"])
    
    with tab1:
        fig_prof = px.line(prof_df, x='year', y=['roa_percent', 'roe_percent'], markers=True, title="Return on Assets & Equity")
        st.plotly_chart(fig_prof, use_container_width=True)
        
    with tab2:
        fig_eff = px.area(eff_df, x='year', y='cost_to_income_ratio', title="Cost-to-Income Efficiency Trend")
        fig_eff.add_hline(y=50, line_dash="dot", line_color="green", annotation_text="Efficiency Benchmark")
        st.plotly_chart(fig_eff, use_container_width=True)

else:
    st.warning("Data not found. Ingesting mock data...")
    from Financial_KPIs_Warehouse.ingestion.generate_robust_data import generate_absa_financials
    generate_absa_financials()
    st.rerun()
