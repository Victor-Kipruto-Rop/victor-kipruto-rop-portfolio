import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
import os

st.set_page_config(page_title="Absa Kenya: Financial & Open Banking Analytics", layout="wide", page_icon="🔴")

# Robust path handling for Streamlit Cloud
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_data(query, snapshot_name):
    try:
        host = "postgres-absa" if os.path.exists("/.dockerenv") else "localhost"
        engine = create_engine(f'postgresql://absa_admin:absa_password@{host}:5432/absa_warehouse')
        return pd.read_sql(query, engine)
    except Exception:
        snapshot_path = os.path.join(BASE_DIR, "dashboards", "snapshots", f"{snapshot_name}.csv")
        if os.path.exists(snapshot_path):
            return pd.read_csv(snapshot_path)
        return pd.DataFrame()

st.title("🔴 Absa Bank Kenya: Integrated Analytics Dashboard")
st.markdown("Comprehensive view of Financial Performance, Risk Management, and Open Banking Adoption.")

# Navigation
tabs = st.tabs(["💰 Financial KPIs", "🛡️ Risk & Capital", "🔌 Open Banking Insights"])

# Tab 1: Financial KPIs
with tabs[0]:
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
        
        c1, c2 = st.columns(2)
        with c1:
            fig_prof = px.line(prof_df, x='year', y=['roa_percent', 'roe_percent'], markers=True, title="Return on Assets & Equity Trends")
            st.plotly_chart(fig_prof, use_container_width=True)
            
        with c2:
            fig_eff = px.area(eff_df, x='year', y='cost_to_income_ratio', title="Cost-to-Income Efficiency Trend")
            fig_eff.add_hline(y=50, line_dash="dot", line_color="green", annotation_text="Efficiency Benchmark")
            st.plotly_chart(fig_eff, use_container_width=True)
    else:
        st.warning("Financial KPI data not found.")

# Tab 2: Risk & Capital
with tabs[1]:
    asset_df = load_data("SELECT * FROM mart_asset_quality ORDER BY year", "mart_asset_quality")
    capital_df = load_data("SELECT * FROM mart_capital_adequacy ORDER BY year", "mart_capital_adequacy")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if not asset_df.empty:
            st.write("### 📉 Asset Quality (NPL Ratio)")
            fig_npl = px.bar(asset_df, x='year', y='npl_ratio_percentage', title="Non-Performing Loans Ratio (%)", color_discrete_sequence=['red'])
            st.plotly_chart(fig_npl, use_container_width=True)
        else:
            st.info("NPL data unavailable.")
            
    with col2:
        if not capital_df.empty:
            st.write("### 🏛️ Capital Adequacy (CAR)")
            fig_car = px.line(capital_df, x='year', y='car_percentage', title="Capital Adequacy Ratio (%)", markers=True)
            fig_car.add_hline(y=14.5, line_dash="dash", line_color="red", annotation_text="Statutory Minimum")
            st.plotly_chart(fig_car, use_container_width=True)
        else:
            st.info("Capital adequacy data unavailable.")

# Tab 3: Open Banking Insights
with tabs[2]:
    activity_df = load_data("SELECT * FROM mart_customer_activity", "mart_customer_activity")
    
    if not activity_df.empty:
        st.write("### ⚡ Open Banking API Usage")
        col1, col2 = st.columns(2)
        
        total_tx = activity_df['transaction_count'].sum()
        total_vol = activity_df['total_volume'].sum()
        
        col1.metric("Total API Transactions", f"{total_tx:,}")
        col2.metric("Total API Volume (KES)", f"{total_vol:,.2f}")
        
        st.markdown("---")
        
        # Trend of activity if activity_date is available and varies
        if 'activity_date' in activity_df.columns:
            activity_df['activity_date'] = pd.to_datetime(activity_df['activity_date'])
            daily_activity = activity_df.groupby('activity_date')['transaction_count'].sum().reset_index()
            fig_activity = px.line(daily_activity, x='activity_date', y='transaction_count', title="Daily API Transaction Volume")
            st.plotly_chart(fig_activity, use_container_width=True)
    else:
        st.info("Open Banking activity data not found. Ensure the API pipeline is running.")

logo_path = os.path.join(BASE_DIR, "images", "absa.png")
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, width=100)
else:
    # Fallback for root execution
    logo_path_root = os.path.join(BASE_DIR, "Absa_Bank_Kenya(PIPELINE)", "images", "absa.png")
    if os.path.exists(logo_path_root):
        st.sidebar.image(logo_path_root, width=100)

st.sidebar.title("Data Controls")
if st.sidebar.button("Refresh Dashboard"):
    st.rerun()

st.sidebar.markdown("""
**Data Sources:**
- FY 2025 Integrated Report
- Pillar 3 Disclosures
- Open Banking API Gateway
""")
