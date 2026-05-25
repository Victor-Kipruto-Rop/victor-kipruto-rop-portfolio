import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
import os

# Page Config
st.set_page_config(page_title="KRA: Revenue & Trade Analytics Hub", layout="wide", page_icon="📊")

# Robust path handling for Streamlit Cloud
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data Loader (Postgres with CSV Fallback)
def load_data(query, snapshot_name, project_subfolder):
    try:
        host = "postgres-kra" if os.path.exists("/.dockerenv") else "localhost"
        engine = create_engine(f'postgresql://kra_admin:kra_password@{host}:5438/kra_warehouse')
        return pd.read_sql(query, engine)
    except Exception:
        # Fallback to snapshots
        snapshot_path = os.path.join(BASE_DIR, project_subfolder, "dashboards", "snapshots", f"{snapshot_name}.csv")
        if os.path.exists(snapshot_path):
            return pd.read_csv(snapshot_path)
        else:
            return pd.DataFrame()

# Sidebar
st.sidebar.title("KRA Analytics Hub")
st.sidebar.markdown("### 📊 National Revenue & Trade")
app_mode = st.sidebar.selectbox("Choose Dashboard", ["Tax Revenue Performance", "Customs & Trade Intelligence", "Macro-Economic Indicators"])

if app_mode == "Tax Revenue Performance":
    st.title("📈 KRA: National Tax Revenue Performance")
    st.markdown("Monitoring actual collections vs. Treasury targets across primary tax heads.")
    
    rev_df = load_data('SELECT * FROM mart_revenue_by_tax_head', 'mart_revenue_by_tax_head', 'Tax_Revenue_Analytics')
    target_df = load_data('SELECT * FROM mart_target_vs_actual', 'mart_target_vs_actual', 'Tax_Revenue_Analytics')

    if not rev_df.empty:
        # Summary Metrics
        latest_year = rev_df['year'].max()
        curr_rev = rev_df[rev_df['year'] == latest_year]
        total_actual = curr_rev['actual_revenue_m_kes'].sum()
        
        c1, c2, c3 = st.columns(3)
        c1.metric(f"Total Revenue ({latest_year})", f"KES {total_actual/1000:,.1f}B")
        
        if not target_df.empty:
            curr_target = target_df[target_df['year'] == latest_year]
            performance = (total_actual / curr_target['target_revenue_m_kes'].sum()) * 100
            c2.metric("Target Achievement", f"{performance:.1f}%")
            c3.metric("Tax Heads Tracked", rev_df['tax_head'].nunique())

        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Revenue Distribution by Tax Head")
            fig_pie = px.pie(curr_rev, names='tax_head', values='actual_revenue_m_kes', hole=0.4, color_discrete_sequence=px.colors.qualitative.Bold)
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with col2:
            st.subheader("Target vs. Actual Variance")
            if not target_df.empty:
                fig_var = px.bar(target_df[target_df['year'] == latest_year], x='tax_head', y=['actual_revenue_m_kes', 'target_revenue_m_kes'], barmode='group', title="Achievement by Sector")
                st.plotly_chart(fig_var, use_container_width=True)

        st.subheader("Annual Revenue Growth Trends")
        fig_line = px.line(rev_df.groupby(['year', 'tax_head'])['actual_revenue_m_kes'].sum().reset_index(), x='year', y='actual_revenue_m_kes', color='tax_head', markers=True)
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.warning("Revenue data not found.")

elif app_mode == "Customs & Trade Intelligence":
    st.title("🚢 KRA: Customs & International Trade")
    st.markdown("Analysis of import/export volumes, duty collection, and HS-code benchmarks.")
    
    trade_df = load_data('SELECT * FROM mart_trade_balance', 'mart_trade_balance', 'Customs_Trade_Pipeline')
    duty_df = load_data('SELECT * FROM mart_duty_collection', 'mart_duty_collection', 'Customs_Trade_Pipeline')

    if not trade_df.empty:
        latest_year = trade_df['year'].max()
        curr_trade = trade_df[trade_df['year'] == latest_year]
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Trade Volume", f"{curr_trade['total_volume_tons'].sum():,.0f} Tons")
        c2.metric("Trade Value", f"KES {curr_trade['total_value_m_kes'].sum()/1000:,.1f}B")
        c3.metric("Duty Collected", f"KES {duty_df['total_duty_m_kes'].sum():,.1f}M")

        st.markdown("---")
        
        st.subheader("Trade Value by Origin Country")
        fig_country = px.bar(duty_df.groupby('origin_country')['total_value_m_kes'].sum().reset_index().sort_values('total_value_m_kes', ascending=False).head(10), 
                             x='origin_country', y='total_value_m_kes', color='total_value_m_kes', color_continuous_scale='Viridis')
        st.plotly_chart(fig_country, use_container_width=True)
        
        st.subheader("Top Commodities by Duty Contribution (HS-Code)")
        hs_df = load_data('SELECT * FROM mart_trade_by_hs_code', 'mart_trade_by_hs_code', 'Customs_Trade_Pipeline')
        if not hs_df.empty:
            fig_hs = px.treemap(hs_df, path=['commodity_description'], values='annual_duty', title="Duty Contribution by Category")
            st.plotly_chart(fig_hs, use_container_width=True)
    else:
        st.warning("Trade data not found.")

else:
    st.title("📉 KRA: Macro-Economic Leading Indicators")
    st.markdown("Insights from the 2026 Economic Survey and KNBS Leading Economic Indicators.")
    
    gdp_df = load_data('SELECT * FROM mart_gdp_growth', 'mart_gdp_growth', 'Tax_Revenue_Analytics')
    ratio_df = load_data('SELECT * FROM mart_gdp_tax_ratio', 'mart_gdp_tax_ratio', 'Tax_Revenue_Analytics')

    if not gdp_df.empty:
        st.subheader("GDP Growth Rates by Industry (2021-2025)")
        # Heatmap of growth rates
        growth_pivot = gdp_df.pivot(index='industry', columns='year', values='growth_rate_percent')
        fig_heat = px.imshow(growth_pivot, text_auto=True, aspect="auto", color_continuous_scale='RdYlGn', title="Industry Growth Heatmap (%)")
        st.plotly_chart(fig_heat, use_container_width=True)
        
        if not ratio_df.empty:
            st.markdown("---")
            st.subheader("Tax-to-GDP Ratio Evolution")
            fig_ratio = px.area(ratio_df, x='year', y='tax_to_gdp_ratio_percent', title="National Tax Efficiency (Tax as % of GDP)")
            fig_ratio.add_hline(y=15, line_dash="dot", line_color="red", annotation_text="SSA Average Benchmark")
            st.plotly_chart(fig_ratio, use_container_width=True)
    else:
        st.warning("Economic indicator data not found.")

# Sidebar Data Sources
st.sidebar.markdown("""
---
**Data Sources:**
- KRA Annual Revenue Reports (2021-2025)
- KNBS 2026 Economic Survey
- UN Comtrade & Rules of Origin Forms
- iTax Business Registration Logs
""")

if st.sidebar.button("Refresh Hub"):
    st.rerun()
