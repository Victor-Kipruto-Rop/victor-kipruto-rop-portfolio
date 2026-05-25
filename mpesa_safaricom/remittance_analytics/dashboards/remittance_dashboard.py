import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Remittance Analytics", layout="wide", page_icon="🌍")

st.title("🌍 Kenya Cross-Border Remittance Intelligence")
st.sidebar.info("Analysis of international money inflows and corridor pricing.")

# Load Data
raw_path = "data/remittances_raw.csv"

if os.path.exists(raw_path):
    df = pd.read_csv(raw_path)
    df['transfer_date'] = pd.to_datetime(df['transfer_date'])
    
    # Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Volume (USD)", f"${df['amount_usd'].sum()/1e6:.1f}M")
    c2.metric("Avg Transfer Fee", f"{ (df['transfer_fee_usd'].sum() / df['amount_usd'].sum() * 100):.2f}%")
    c3.metric("Top Sender Country", df.groupby('sender_country')['amount_usd'].sum().idxmax())

    st.markdown("---")

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("💰 Inflow Volume by Country (USD)")
        fig_vol = px.bar(df.groupby('sender_country')['amount_usd'].sum().reset_index().sort_values('amount_usd'), 
                         x='amount_usd', y='sender_country', orientation='h', color='amount_usd',
                         color_continuous_scale='Blues')
        st.plotly_chart(fig_vol, use_container_width=True)
        
    with col_b:
        st.subheader("📈 Monthly Inflow Trend (USD)")
        monthly_df = df.set_index('transfer_date').resample('M')['amount_usd'].sum().reset_index()
        fig_trend = px.area(monthly_df, x='transfer_date', y='amount_usd', title="6-Month Inflow Curve")
        st.plotly_chart(fig_trend, use_container_width=True)

    st.subheader("💸 Fee Benchmark by Corridor")
    df['fee_percent'] = (df['transfer_fee_usd'] / df['amount_usd']) * 100
    fig_fee = px.box(df, x='sender_country', y='fee_percent', color='sender_country', title="Transfer Fee Percentage Distribution")
    st.plotly_chart(fig_fee, use_container_width=True)

else:
    st.warning("Generate remittance data to see analytics.")
