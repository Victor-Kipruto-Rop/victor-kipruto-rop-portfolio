import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Merchant Intelligence", layout="wide", page_icon="🏢")

st.title("🏢 M-Pesa Merchant Intelligence Platform")
st.sidebar.info("Operational analytics and RFM segmentation for M-Pesa merchants.")

# Load Data
raw_path = "data/merchants_raw.csv"

if os.path.exists(raw_path):
    df = pd.read_csv(raw_path)
    
    # KPIs
    c1, c2, c3 = st.columns(3)
    c1.metric("Active Merchants", len(df))
    c2.metric("Avg Monthly Vol", f"KES {df['monthly_volume_kes'].mean()/1e3:.1f}K")
    c3.metric("High Risk Churners", len(df[df['churn_risk_score'] > 0.7]))

    st.markdown("---")

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("📊 Merchant Segment Distribution")
        df['segment'] = df['monthly_volume_kes'].apply(lambda x: 'Enterprise' if x > 1e7 else ('Key Account' if x > 1e6 else 'SME'))
        fig_seg = px.pie(df, names='segment', hole=0.4, color_discrete_sequence=px.colors.sequential.YlOrBr_r)
        st.plotly_chart(fig_seg, use_container_width=True)
        
    with col_b:
        st.subheader("📍 County Merchant Density")
        fig_map = px.bar(df.groupby('county')['merchant_id'].count().reset_index().sort_values('merchant_id'), 
                         x='merchant_id', y='county', orientation='h', title="Merchants per County")
        st.plotly_chart(fig_map, use_container_width=True)

    st.subheader("🔥 Churn Risk Leaderboard (Top SME Risks)")
    st.dataframe(df[df['churn_risk_score'] > 0.6].sort_values('churn_risk_score', ascending=False).head(10), use_container_width=True)

else:
    st.warning("Generate merchant data to see analytics.")
