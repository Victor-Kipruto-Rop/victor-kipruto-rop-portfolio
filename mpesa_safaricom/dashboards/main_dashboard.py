import streamlit as st
import pandas as pd
import plotly.express as px
import os
from sqlalchemy import create_engine

st.set_page_config(page_title="M-Pesa Flagship Analytics", layout="wide", page_icon="🟢")

# Database Connection
def get_engine():
    db_host = os.getenv('DB_HOST', 'localhost')
    db_name = os.getenv('DB_NAME', 'mpesa_warehouse')
    db_user = os.getenv('DB_USER', 'mpesa_admin')
    db_pass = os.getenv('DB_PASSWORD', 'mpesa_password')
    # Local fallback port is 5439 for external access
    db_port = '5432' if db_host == 'postgres-mpesa' else '5439'
    return create_engine(f'postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}')

@st.cache_data(ttl=60)
def load_data(query):
    try:
        engine = get_engine()
        return pd.read_sql(query, engine)
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        return pd.DataFrame()

# Sidebar
st.sidebar.title("🟢 M-Pesa Flagship Hub")
st.sidebar.markdown("""
This dashboard provides real-time insights into M-Pesa transactions, fraud patterns, and regional performance.
""")
st.sidebar.info("Data Source: Kafka Stream → PostgreSQL → dbt")

# Main Dashboard
st.title("🚀 M-Pesa Real-Time Financial Intelligence")

# KPIs
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_tx = load_data("SELECT count(*) as count FROM raw_transactions")
    val = total_tx['count'].iloc[0] if not total_tx.empty else 0
    st.metric("Total Transactions", f"{val:,}")

with col2:
    total_vol = load_data("SELECT sum(amount) as vol FROM raw_transactions")
    val = total_vol['vol'].iloc[0] if not total_vol.empty else 0
    st.metric("Total Volume (KES)", f"{val/1e6:,.1f}M")

with col3:
    fraud_rate = load_data("SELECT avg(is_fraud)*100 as rate FROM raw_transactions")
    val = fraud_rate['rate'].iloc[0] if not fraud_rate.empty else 0
    st.metric("Fraud Rate", f"{val:.2f}%", delta="-0.05%", delta_color="inverse")

with col4:
    freshness = load_data("SELECT max(ingested_at) as last_load FROM raw_transactions")
    val = freshness['last_load'].iloc[0] if not freshness.empty else "N/A"
    st.metric("Data Freshness", str(val)[:19])

st.markdown("---")

# Charts
c1, c2 = st.columns(2)

with c1:
    st.subheader("📍 Transaction Volume by County")
    county_df = load_data("SELECT * FROM mart_county_performance")
    if not county_df.empty:
        fig = px.bar(county_df.sort_values('total_volume_kes', ascending=False), 
                     x='county', y='total_volume_kes', color='total_volume_kes',
                     color_continuous_scale='Greens', labels={'total_volume_kes': 'Volume (KES)'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Waiting for dbt mart data...")

with c2:
    st.subheader("🛡️ Fraud Risk by Time of Day")
    fraud_df = load_data("SELECT * FROM mart_fraud_velocity_metrics")
    if not fraud_df.empty:
        fig = px.density_heatmap(fraud_df, x='time_bin', y='county', z='fraud_rate_percentage',
                                 color_continuous_scale='Reds', title="Fraud Concentration Heatmap")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Waiting for fraud mart data...")

# Live Feed
st.subheader("📡 Recent Real-Time Transactions")
recent_tx = load_data("SELECT transaction_id, timestamp, amount, transaction_type, county, is_fraud FROM raw_transactions ORDER BY timestamp DESC LIMIT 10")
if not recent_tx.empty:
    st.dataframe(recent_tx, use_container_width=True)

if st.sidebar.button("Force Refresh"):
    st.rerun()
