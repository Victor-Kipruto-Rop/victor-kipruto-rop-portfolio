import streamlit as st
import pandas as pd
import plotly.express as px
import os
from sqlalchemy import create_engine

st.set_page_config(page_title="M-Pesa Agent Analytics", layout="wide", page_icon="🏪")

def load_data(query, snapshot_name):
    # Standard portfolio loader
    try:
        db_host = os.getenv('DB_HOST', 'localhost')
        engine = create_engine(f'postgresql://mpesa_admin:mpesa_password@{db_host}:5439/mpesa_warehouse')
        return pd.read_sql(query, engine)
    except:
        path = f"data/{snapshot_name}.csv"
        return pd.read_csv(path) if os.path.exists(path) else pd.DataFrame()

st.title("🏪 M-Pesa Agent Liquidity & Performance")

# Data
df_agents = load_data("SELECT * FROM stg_agents", "agents_raw")

if not df_agents.empty:
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Agents", len(df_agents))
    col2.metric("Total Float", f"KES {df_agents['float_balance'].sum()/1e6:.1f}M")
    col3.metric("Critical Float Alerts", len(df_agents[df_agents['float_balance'] < 5000]))

    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📍 Agent Distribution by County")
        fig_county = px.pie(df_agents, names='county', hole=0.4, color_discrete_sequence=px.colors.sequential.Greens_r)
        st.plotly_chart(fig_county, use_container_width=True)
    
    with c2:
        st.subheader("💰 Float Balance vs. Activity")
        fig_scatter = px.scatter(df_agents, x='float_balance', y='txns_today', color='county', size='float_balance', 
                                 hover_name='agent_id', title="Daily Transactions vs. Float Balance")
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.subheader("🚨 Critical Low Float Alert List")
    st.dataframe(df_agents[df_agents['float_balance'] < 5000].sort_values('float_balance'), use_container_width=True)

else:
    st.info("Ingest agent data to see analytics.")
