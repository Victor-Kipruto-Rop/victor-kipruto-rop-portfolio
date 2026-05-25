import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Page Config
st.set_page_config(page_title="Kenya Banking & Telecom: Integrated Analytics", layout="wide", page_icon="🏦")

# Helper to load snapshot data
def load_snapshot(project, snapshot_name):
    paths = [
        f"{project}/dashboards/snapshots/{snapshot_name}.csv",
        f"{project}/snapshots/{snapshot_name}.csv"
    ]
    for path in paths:
        if os.path.exists(path):
            return pd.read_csv(path)
    return pd.DataFrame()

# Sidebar Navigation
st.sidebar.title("Sector Navigator")
bank_selection = st.sidebar.selectbox("Select View", 
    ["Executive Summary (2025)", "Sector Overview (DWH)", "AML Monitoring Engine", "KRA Tax Revenue", "M-Pesa Fraud Monitor", "KCB Group", "Absa Bank Kenya", "Equity Group", "Safaricom PLC"])

st.sidebar.markdown("---")
st.sidebar.button("Refresh Snapshots", on_click=lambda: st.session_state.clear())

if bank_selection == "Executive Summary (2025)":
    st.title("🏦 Kenya Banking Sector: 2025 Executive Summary")
    st.markdown("Comparative performance analysis of Tier 1 Banks based on FY 2025 Audited Results.")
    
    # Load Data
    kcb_df = load_snapshot("KCB_Group(ETL)/Financial_Performance_Tracker", "mart_roe_roa")
    absa_df = load_snapshot("Absa_Bank_Kenya(PIPELINE)", "mart_profitability")
    equity_df = load_snapshot("Equity_Group(PIPELINE_ETL)", "mart_subsidiary_performance")
    saf_df = load_snapshot("Safaricom(PIPELINE)", "mart_financial_results")
    
    # Filter for 2025
    kcb_2025 = kcb_df[(kcb_df['year'] == 2025) & (kcb_df['subsidiary'] == 'KCB Group Consolidated')] if not kcb_df.empty else pd.DataFrame()
    absa_2025 = absa_df[absa_df['year'] == 2025] if not absa_df.empty else pd.DataFrame()
    saf_2025 = saf_df[saf_df['period'] == 'FY 2025 (E)'] if not saf_df.empty else pd.DataFrame()
    
    # Prepare comparison table
    summary_data = []
    if not kcb_2025.empty:
        summary_data.append({
            "Institution": "KCB Group",
            "Net Profit (M KES)": kcb_2025['net_profit_m_kes'].iloc[0],
            "Total Assets (M KES)": kcb_2025['total_assets_m_kes'].iloc[0]
        })
    if not absa_2025.empty:
        summary_data.append({
            "Institution": "Absa Kenya",
            "Net Profit (M KES)": absa_2025['net_profit'].iloc[0],
            "Total Assets (M KES)": absa_2025['total_assets'].iloc[0]
        })
    if not saf_2025.empty:
        summary_data.append({
            "Institution": "Safaricom PLC",
            "Net Profit (M KES)": saf_2025['net_profit_m_kes'].iloc[0],
            "Total Assets (M KES)": 380000.0 # Estimate
        })
        
    if summary_data:
        comp_df = pd.DataFrame(summary_data)
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("### 💰 Profitability Comparison")
            fig_prof = px.bar(comp_df, x="Institution", y="Net Profit (M KES)", color="Institution", text_auto='.2s')
            st.plotly_chart(fig_prof, use_container_width=True)
            
        with col2:
            st.write("### 📊 Market Valuation Matrix")
            fig_val = px.scatter(comp_df, x='Total Assets (M KES)', y='Net Profit (M KES)', size='Net Profit (M KES)', color='Institution', hover_name='Institution')
            st.plotly_chart(fig_val, use_container_width=True)
            
        st.write("### 📊 Consolidated 2025 Metrics")
        st.dataframe(comp_df.style.format({
            "Net Profit (M KES)": "{:,.0f}",
            "Total Assets (M KES)": "{:,.0f}"
        }), use_container_width=True)
    else:
        st.warning("No 2025 snapshot data found. Please run 'create_all_snapshots.py' first.")

elif bank_selection == "Sector Overview (DWH)":
    st.title("🏦 Kenya Banking Sector: Consolidated Analytics")
    st.info("Displaying aggregated metrics for all 38+ licensed banks (CBK Supervision Reports).")
    st.markdown("[Open Detailed Sector Dashboard](http://localhost:8504)")

elif bank_selection == "AML Monitoring Engine":
    st.title("🛡️ Kenya Banking Sector: AML Transaction Monitoring")
    st.info("Rules-based detection of suspicious financial activities across the sector.")
    st.markdown("[Open AML Monitoring Dashboard](http://localhost:8505)")

elif bank_selection == "KRA Tax Revenue":
    st.title("🇰🇪 KRA: Integrated Analytics Suite")
    st.info("Monitoring national tax collection performance and fiscal trends.")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### [📈 Tax Revenue Warehouse](http://localhost:8506)")
    with c2:
        st.markdown("### [🚢 Customs & Trade Intelligence](http://localhost:8507)")

elif bank_selection == "M-Pesa Fraud Monitor":
    st.title("🕵️ M-Pesa: Fraud & Anomaly Detection")
    st.info("Real-time ML-powered fraud scoring for mobile money transactions.")
    st.markdown("### [🕵️ Fraud Detection](http://localhost:8510)")

elif bank_selection == "KCB Group":
    st.title("🦁 KCB Group Integrated Analytics")
    st.markdown("[Open KCB Financial Dashboard](http://localhost:8503)")
    
elif bank_selection == "Absa Bank Kenya":
    st.title("🏦 Absa Kenya Financial Insights")
    st.markdown("[Open Absa Financial Dashboard](http://localhost:8501)")

elif bank_selection == "Equity Group":
    st.title("🌍 Equity Group Pan-Africa Insights")
    st.markdown("[Open Equity Integrated Dashboard](http://localhost:8502)")

elif bank_selection == "Safaricom PLC":
    st.title("📱 Safaricom PLC Integrated Analytics")
    st.markdown("[Open Safaricom Financial & Network Dashboard](http://localhost:8513)")
