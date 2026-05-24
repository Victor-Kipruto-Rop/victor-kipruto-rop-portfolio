import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import os

st.set_page_config(page_title="KRA: Tax Revenue Analytics", layout="wide", page_icon="🇰🇪")

def load_data(query, snapshot_name):
    try:
        host = "postgres" if os.path.exists("/.dockerenv") else "localhost"
        engine = create_engine(f'postgresql://kra_admin:kra_password@{host}:5438/kra_warehouse')
        return pd.read_sql(query, engine)
    except Exception:
        # Fallback to snapshots
        snapshot_path = f"dashboards/snapshots/{snapshot_name}.csv"
        if os.path.exists(snapshot_path):
            return pd.read_csv(snapshot_path)
        return pd.DataFrame()

st.title("🇰🇪 KRA: Tax Revenue Analytics Warehouse")
st.markdown("Monitoring tax collection performance across different tax heads and historical trends.")

revenue_head = load_data("SELECT * FROM mart_revenue_by_tax_head ORDER BY year DESC", "mart_revenue_by_tax_head")
performance_trend = load_data("SELECT * FROM mart_target_vs_actual ORDER BY year, month", "mart_target_vs_actual")

if not revenue_head.empty:
    latest_year = revenue_head['year'].max()
    latest_data = revenue_head[revenue_head['year'] == latest_year]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Revenue (B KES)", f"{latest_data['annual_actual_revenue'].sum()/1000:,.1f}B")
    col2.metric("Target Performance %", f"{(latest_data['annual_actual_revenue'].sum() / latest_data['annual_target_revenue'].sum() * 100):,.1f}%")
    col3.metric("Fiscal Year", latest_year)

    st.markdown("---")
    
    tab1, tab2 = st.tabs(["Revenue Breakdown", "Performance Trends"])
    
    with tab1:
        st.subheader(f"Revenue by Tax Head ({latest_year})")
        fig_pie = px.pie(latest_data, names='tax_head', values='annual_actual_revenue', hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)
        
        st.subheader("Tax Head Efficiency")
        fig_bar = px.bar(latest_data, x='tax_head', y='performance_percent', color='performance_percent', color_continuous_scale='Greens')
        fig_bar.add_hline(y=100, line_dash="dot", line_color="red", annotation_text="Target")
        st.plotly_chart(fig_bar, use_container_width=True)

    with tab2:
        st.subheader("Historical Revenue Growth")
        # Aggregated yearly trend
        yearly_trend = revenue_head.groupby('year')['annual_actual_revenue'].sum().reset_index()
        fig_trend = px.line(yearly_trend, x='year', y='annual_actual_revenue', markers=True)
        st.plotly_chart(fig_trend, use_container_width=True)
        
        if not performance_trend.empty:
            st.subheader("Monthly Performance vs Target")
            fig_perf = px.line(performance_trend, x='year', y='monthly_performance', markers=True)
            fig_perf.add_hline(y=100, line_dash="dot", line_color="red")
            st.plotly_chart(fig_perf, use_container_width=True)

else:
    st.warning("No data found. Please run the pipeline first.")
