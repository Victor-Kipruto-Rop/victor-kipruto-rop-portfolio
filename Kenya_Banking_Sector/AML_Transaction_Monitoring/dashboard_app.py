import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys

# Ensure we can import from src
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from rules_engine import AMLRulesEngine

st.set_page_config(page_title="Kenya Banking Sector: AML Monitoring", layout="wide", page_icon="🛡️")

st.title("🛡️ AML / Transaction Monitoring Rules Engine")
st.markdown("Automated detection of suspicious financial patterns based on CBK guidelines.")

data_path = "Kenya_Banking_Sector/AML_Transaction_Monitoring/data/synthetic_transactions.csv"

if not os.path.exists(data_path):
    st.info("Generating synthetic test data...")
    from ingestion.synthetic_generator import generate_aml_test_data
    generate_aml_test_data()

engine = AMLRulesEngine(data_path)
alerts = engine.get_all_alerts()

if alerts:
    alerts_df = pd.DataFrame(alerts)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Alerts", len(alerts_df))
    col2.metric("High Severity", len(alerts_df[alerts_df['severity'] == 'High']))
    col3.metric("Medium Severity", len(alerts_df[alerts_df['severity'] == 'Medium']))

    st.markdown("---")
    
    tab1, tab2 = st.tabs(["Alert Queue", "Risk Analytics"])
    
    with tab1:
        st.subheader("Suspicious Activity Report (SAR) Queue")
        st.dataframe(alerts_df, use_container_width=True)
        
    with tab2:
        st.subheader("Risk Distribution by Rule")
        fig_rule = px.pie(alerts_df, names='rule', hole=0.4, color_discrete_sequence=px.colors.sequential.Reds_r)
        st.plotly_chart(fig_rule, use_container_width=True)
        
        if not engine.df.empty:
            st.subheader("Transaction Volume Heatmap (by Bank)")
            bank_vol = engine.df.groupby('bank_id')['amount'].sum().reset_index()
            fig_bank = px.bar(bank_vol, x='bank_id', y='amount', color='amount', color_continuous_scale='Reds')
            st.plotly_chart(fig_bank, use_container_width=True)

else:
    st.success("No suspicious patterns detected in the current period.")
