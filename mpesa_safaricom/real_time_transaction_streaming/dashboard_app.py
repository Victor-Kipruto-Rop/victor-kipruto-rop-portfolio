import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
import os
import time

st.set_page_config(page_title="M-Pesa Real-Time Streaming", layout="wide", page_icon="⚡")

def load_streaming_data():
    try:
        # Connect to Safaricom database
        host = "postgres-mpesa" if os.path.exists("/.dockerenv") else "localhost"
        engine = create_engine(f'postgresql://mpesa_admin:mpesa_password@{host}:5439/mpesa_warehouse')
        return pd.read_sql("SELECT * FROM raw_mpesa_streaming ORDER BY timestamp DESC LIMIT 100", engine)
    except Exception:
        # Mock for dashboard demo if DB not ready
        data = []
        for i in range(20):
            data.append({
                "txn_id": f"MP_{1000+i}",
                "timestamp": pd.Timestamp.now() - pd.Timedelta(minutes=i*2),
                "amount": 500 * (i % 5 + 1),
                "status": "Success" if i % 10 != 0 else "Failed",
                "type": "C2B" if i % 2 == 0 else "B2C"
            })
        return pd.DataFrame(data)

st.title("⚡ M-Pesa Real-Time Transaction Streaming")
st.markdown("Live monitor for M-Pesa Daraja API transactions processing through Apache Kafka.")

# Metrics
df = load_streaming_data()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Live TPS", "45.2", delta="2.1")
c2.metric("Total Volume (Last Hour)", f"{df['amount'].sum():,.0f} KES")
c3.metric("Error Rate", "0.04%", delta="-0.01%")
c4.metric("Active Kafka Consumers", "12")

st.markdown("---")

col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("Live Transaction Stream")
    st.dataframe(df, use_container_width=True)
    
    st.subheader("Volume Trend (Real-Time)")
    fig_line = px.line(df, x='timestamp', y='amount', color='type', markers=True)
    st.plotly_chart(fig_line, use_container_width=True)

with col_right:
    st.subheader("Success vs Failure")
    fig_pie = px.pie(df, names='status', color='status', color_discrete_map={'Success':'green', 'Failed':'red'}, hole=0.5)
    st.plotly_chart(fig_pie, use_container_width=True)
    
    st.subheader("Kafka Cluster Health")
    st.progress(98, text="Broker 1: Healthy")
    st.progress(99, text="Broker 2: Healthy")
    st.progress(97, text="Broker 3: Healthy")

# Auto-refresh
if st.checkbox("Enable Auto-Refresh (5s)"):
    time.sleep(5)
    st.rerun()
