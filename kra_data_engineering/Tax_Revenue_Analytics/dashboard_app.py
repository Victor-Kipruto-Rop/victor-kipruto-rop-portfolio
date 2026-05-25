import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import os

st.set_page_config(page_title="KRA: Tax Revenue Analytics", layout="wide", page_icon="🇰🇪")

def load_data(query, snapshot_name):
    try:
        # Check if running inside Docker
        if os.path.exists("/.dockerenv"):
            host = "postgres-kra"
            port = "5432"
        else:
            host = "localhost"
            port = "5438"
            
        engine = create_engine(f'postgresql://kra_admin:kra_password@{host}:{port}/kra_warehouse')
        return pd.read_sql(query, engine)
    except Exception as e:
        # Fallback to snapshots
        st.sidebar.warning(f"Live DB connection failed: {e}. Using snapshots.")
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
    
    tab1, tab2, tab3 = st.tabs(["Revenue Breakdown", "Performance Trends", "Macro Context"])
    
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
        yearly_trend = revenue_head.groupby('year')['annual_actual_revenue'].sum().reset_index()
        fig_trend = px.line(yearly_trend, x='year', y='annual_actual_revenue', markers=True)
        st.plotly_chart(fig_trend, use_container_width=True)
        
        if not performance_trend.empty:
            st.subheader("Monthly Performance vs Target")
            fig_perf = px.line(performance_trend, x='year', y='monthly_performance', markers=True)
            fig_perf.add_hline(y=100, line_dash="dot", line_color="red")
            st.plotly_chart(fig_perf, use_container_width=True)

    with tab3:
        st.subheader("National Economic Indicators (KNBS)")
        macro_df = load_data("SELECT * FROM macro_economic_indicators", "macro_economic_indicators")
        if not macro_df.empty:
            c1, c2 = st.columns(2)
            with c1:
                infl = macro_df[macro_df['indicator'] == 'Inflation Rate']
                if not infl.empty:
                    st.metric("Current Inflation Rate", f"{infl['value'].iloc[0]}%", help="Source: KNBS Leading Indicators Feb 2023")
            
            with c2:
                trade = macro_df[macro_df['indicator'].str.contains("Total")]
                if not trade.empty:
                    st.write("**Trade Volume (Feb 2023)**")
                    st.dataframe(trade[['indicator', 'value', 'unit']], hide_index=True)
            
            st.info("Macroeconomic indicators provide context for tax revenue performance, especially for VAT and Customs collections.")

else:
    st.warning("No data found. Please run the pipeline first.")
