import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
import os

# Page Config
st.set_page_config(page_title="Kenya Banking Sector: Integrated Analytics", layout="wide", page_icon="🏦")

# Sidebar Navigation
st.sidebar.title("Sector Navigator")
bank_selection = st.sidebar.selectbox("Select Institution", ["Sector Overview (DWH)", "AML Monitoring Engine", "KRA Tax Revenue", "M-Pesa Fraud Monitor", "KCB Group", "Absa Bank Kenya", "Equity Group"])

st.sidebar.markdown("---")
st.sidebar.button("Refresh Data", on_click=lambda: st.session_state.clear())

# Data Loader Helper
def get_engine(db_name, user, password, port=5432):
    host = "postgres" if os.path.exists("/.dockerenv") else "localhost"
    return create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db_name}')

if bank_selection == "Sector Overview (DWH)":
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
        st.write("Track collections vs Treasury targets across all tax heads.")

        st.markdown("### [🚢 Customs & Trade Intelligence](http://localhost:8507)")
        st.write("Monitor import/export volumes and duty collection risk.")

    with c2:
        st.markdown("### [📉 VAT Compliance Gap](http://localhost:8508)")
        st.write("Sector-level analysis of VAT collection efficiency.")

        st.markdown("### [🏢 iTax Business Registration](http://localhost:8509)")
        st.write("Track business formation rates and taxpayer density.")

elif bank_selection == "M-Pesa Fraud Monitor":
    st.title("🕵️ M-Pesa: Fraud & Anomaly Detection")
    st.info("Real-time ML-powered fraud scoring for mobile money transactions.")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### [🕵️ Fraud Detection](http://localhost:8510)")
        st.write("XGBoost-powered fraud scoring.")
    with c2:
        st.markdown("### [⚡ Real-Time Streaming](http://localhost:8511)")
        st.write("Live Kafka-based transaction monitor.")
    with c3:
        st.markdown("### [🗺️ Agent Network](http://localhost:8512)")
        st.write("Geospatial density and liquidity maps.")

elif bank_selection == "KCB Group":

    st.title("🦁 KCB Group Integrated Analytics")
    st.info("Displaying KCB Group Consolidated Performance and M-Pesa Loan Analytics.")
    
elif bank_selection == "Absa Bank Kenya":
    st.title("🏦 Absa Kenya Financial Insights")
    st.info("Displaying Absa Kenya Financial KPIs and Open Banking Analytics.")

elif bank_selection == "Equity Group":
    st.title("🌍 Equity Group Pan-Africa Insights")
    st.info("Displaying Equity Group Digital Adoption and Regional Consolidation.")
