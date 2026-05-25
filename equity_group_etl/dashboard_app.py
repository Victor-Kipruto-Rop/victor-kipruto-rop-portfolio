import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
import os

st.set_page_config(page_title="Equity Group: Integrated Pan-Africa Analytics", layout="wide", page_icon="🏦")

# Robust path handling for Streamlit Cloud
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_data(query, snapshot_name, project_subfolder="."):
    try:
        host = "postgres-equity" if os.path.exists("/.dockerenv") else "localhost"
        engine = create_engine(f'postgresql://equity_admin:equity_password@{host}:5441/equity_warehouse')
        return pd.read_sql(query, engine)
    except Exception:
        snapshot_path = os.path.join(BASE_DIR, project_subfolder, "dashboards", "snapshots", f"{snapshot_name}.csv")
        if os.path.exists(snapshot_path):
            return pd.read_csv(snapshot_path)
        return pd.DataFrame()

st.title("🏦 Equity Group: Integrated Pan-Africa Financial Hub")
st.markdown("Consolidated real-time monitoring of regional markets and Kenya-specific transaction ecosystems.")

# Navigation Tabs
tabs = st.tabs(["🌍 Regional Performance", "🇰🇪 Equity Kenya Transactions", "📱 Digital & Equitel Analytics", "📊 Market Comparison"])

# Tab 1: Regional Performance
with tabs[0]:
    perf_df = load_data("SELECT * FROM mart_subsidiary_performance ORDER BY year", "mart_subsidiary_performance")

    if not perf_df.empty:
        latest_year = perf_df['year'].max()
        latest_data = perf_df[perf_df['year'] == latest_year]
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Group Total Assets", f"KES {latest_data['total_assets_m_kes'].sum()/1000:,.1f}B")
        col2.metric("Group Net Profit", f"KES {latest_data['profit_after_tax_m_kes'].sum()/1000:,.1f}B")
        col3.metric("Digital Channels", f"{latest_data['digital_txn_percentage'].mean():,.1f}%")
        col4.metric("Reporting Markets", latest_data['subsidiary'].nunique())

        st.markdown("---")
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Asset Distribution by Market")
            fig_pie = px.pie(latest_data, names='subsidiary', values='total_assets_m_kes', hole=0.4,
                             color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_pie, use_container_width=True)
        with c2:
            st.subheader("Profitability Contribution (KES M)")
            fig_bar = px.bar(latest_data.sort_values('profit_after_tax_m_kes'), x='subsidiary', y='profit_after_tax_m_kes', 
                             color='profit_after_tax_m_kes', color_continuous_scale='Reds')
            st.plotly_chart(fig_bar, use_container_width=True)
            
        st.subheader("Profit Growth Trends by Region")
        fig_line = px.line(perf_df, x='year', y='profit_after_tax_m_kes', color='subsidiary', markers=True)
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.warning("Regional performance data not found.")

# Tab 2: Equity Kenya Transactions (New)
with tabs[1]:
    st.subheader("🇰🇪 Equity Bank Kenya: Transaction Ecosystem")
    
    kenya_sub = "Equity_Kenya_Transaction_Analytics"
    channel_df = load_data("SELECT * FROM mart_kenya_channel_performance", "mart_kenya_channel_performance", kenya_sub)
    county_df = load_data("SELECT * FROM mart_kenya_county_activity", "mart_kenya_county_activity", kenya_sub)
    trends_df = load_data("SELECT * FROM mart_kenya_transaction_trends", "mart_kenya_transaction_trends", kenya_sub)

    if not channel_df.empty:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.write("#### Channel Mix")
            fig_chan = px.pie(channel_df, names='channel', values='total_volume_kes', hole=0.5, title="Volume by Channel")
            st.plotly_chart(fig_chan, use_container_width=True)
            
        with col2:
            st.write("#### Transaction Trends (2025)")
            if not trends_df.empty:
                trends_df['date'] = pd.to_datetime(trends_df['date'])
                fig_trend = px.line(trends_df, x='date', y='total_volume', title="Daily Transaction Volume (KES)")
                st.plotly_chart(fig_trend, use_container_width=True)

        st.markdown("---")
        c3, c4 = st.columns(2)
        with c3:
            st.write("#### Activity by County")
            fig_county = px.bar(county_df.sort_values('volume_kes', ascending=False), x='county', y='volume_kes', color='volume_kes', color_continuous_scale='Reds')
            st.plotly_chart(fig_county, use_container_width=True)
        with c4:
            st.write("#### Channel Efficiency")
            fig_eff = px.bar(channel_df, x='channel', y='avg_transaction_value', text_auto='.2s', title="Avg Transaction Value by Channel (KES)")
            st.plotly_chart(fig_eff, use_container_width=True)
    else:
        st.info("Kenya-specific transaction data not found.")

# Tab 3: Digital & Equitel Analytics
with tabs[2]:
    adoption_df = load_data("SELECT * FROM mart_adoption_curve", "mart_adoption_curve")
    arpu_df = load_data("SELECT * FROM mart_arpu_benchmark", "mart_arpu_benchmark")
    
    if not adoption_df.empty:
        st.subheader("Equitel & EazzyPay Transaction Growth")
        fig_adoption = px.area(adoption_df, x='period', y='transaction_count', 
                               title="Growth of Digital Banking Transactions",
                               labels={'transaction_count': 'Monthly Transactions', 'period': 'Year-Month'})
        st.plotly_chart(fig_adoption, use_container_width=True)
        
        if not arpu_df.empty:
            st.markdown("---")
            st.subheader("Revenue per User (ARPU) Trends")
            fig_arpu = px.line(arpu_df, x='period', y='arpu_kes', markers=True,
                               title="Average Revenue Per User (KES)",
                               labels={'arpu_kes': 'ARPU (KES)', 'period': 'Year-Month'})
            st.plotly_chart(fig_arpu, use_container_width=True)
    else:
        st.info("Mobile banking analytics data unavailable.")

# Tab 4: Market Comparison
with tabs[3]:
    comp_df = load_data("SELECT * FROM mart_subsidiary_comparison", "mart_subsidiary_comparison")
    
    if not comp_df.empty:
        st.subheader("Regional Profit Contribution Analysis")
        fig_contrib = px.bar(comp_df, x='subsidiary', y='contribution_percentage', 
                             color='subsidiary', text_auto='.2f',
                             title="Subsidiary Contribution to Group Profit (%)",
                             labels={'contribution_percentage': 'Contribution (%)'})
        st.plotly_chart(fig_contrib, use_container_width=True)
        
        st.markdown("---")
        st.subheader("USD vs KES Profit Comparison")
        fig_curr = px.bar(comp_df, x='subsidiary', y=['profit_usd', 'profit_kes'], 
                          title="Profitability by Currency", barmode='group')
        st.plotly_chart(fig_curr, use_container_width=True)
    else:
        st.info("Comparison matrix data not found.")

# Sidebar
logo_path = os.path.join(BASE_DIR, "images", "pan.png")
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, width=150)
else:
    logo_path_root = os.path.join(BASE_DIR, "Equity_Group(PIPELINE_ETL)", "images", "pan.png")
    if os.path.exists(logo_path_root):
        st.sidebar.image(logo_path_root, width=150)

st.sidebar.title("Data Controls")
if st.sidebar.button("Refresh Results"):
    st.rerun()

st.sidebar.markdown("""
**Data Sources:**
- Equity Bank Kenya Transaction Logs (2025)
- Equity Group FY 2025 Audited Reports
- CBK Regional Supervision Disclosures
- Equitel/EazzyPay Ingestion Logs
""")

st.sidebar.info("Dashboard integrates Pan-Africa Consolidation, Kenya Transaction Analytics, and Mobile Banking projects.")
