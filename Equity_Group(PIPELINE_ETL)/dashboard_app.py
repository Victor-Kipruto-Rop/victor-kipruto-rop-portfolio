import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
import os

# Page Config
st.set_page_config(page_title="Equity Group Pan-Africa Insights", layout="wide", page_icon="🌍")

# Data Loader (Postgres with CSV Fallback)
def load_data(query, db_name, snapshot_name):
    try:
        # Try local DB first (Docker environment)
        host = "postgres" if os.path.exists("/.dockerenv") else "localhost"
        engine = create_engine(f'postgresql://equity_admin:equity_password@{host}:5432/{db_name}')
        return pd.read_sql(query, engine)
    except Exception:
        # Fallback to local snapshots (Streamlit Cloud mode)
        snapshot_path = f"dashboards/snapshots/{snapshot_name}.csv"
        if os.path.exists(snapshot_path):
            return pd.read_csv(snapshot_path)
        else:
            st.error(f"Data source not found: {snapshot_name}")
            return pd.DataFrame()

# Sidebar
st.sidebar.title("Equity Group Platform")
st.sidebar.image("https://upload.wikimedia.org/wikipedia/en/thumb/5/52/Equity_Bank_Logo.svg/1200px-Equity_Bank_Logo.svg.png", width=150)
app_mode = st.sidebar.selectbox("Choose Dashboard", ["Equitel & EazzyPay", "Pan-Africa Consolidation"])

if app_mode == "Equitel & EazzyPay":
    st.title("📱 Equitel & EazzyPay: Digital Adoption")
    
    # Load Data via Portable Loader
    adoption = load_data('SELECT * FROM mart_adoption_curve ORDER BY period', 'equitel_analytics', 'mart_adoption_curve')
    arpu = load_data('SELECT * FROM mart_arpu_benchmark ORDER BY period', 'equitel_analytics', 'mart_arpu_benchmark')
    cross_sell = load_data('SELECT * FROM mart_cross_sell_rate ORDER BY period', 'equitel_analytics', 'mart_cross_sell_rate')
    product_mix = load_data('SELECT * FROM mart_product_mix ORDER BY period', 'equitel_analytics', 'mart_product_mix')

    if not adoption.empty:
        # Metrics
        m1, m2, m3 = st.columns(3)
        latest_subscribers = product_mix['total_base'].iloc[-1]
        latest_arpu = arpu['arpu_kes'].iloc[-1]
        
        m1.metric("Total Subscribers", f"{latest_subscribers:,}")
        m2.metric("EazzyPay ARPU (KES)", f"{latest_arpu:.2f}")
        m3.metric("Growth Rate (MoM)", f"{adoption['growth_rate'].iloc[-1]:.1f}%")

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Transaction Velocity (Adoption Curve)")
            fig_adopt = px.line(adoption, x='period', y='transaction_count', markers=True, color_discrete_sequence=['#8B0000'])
            fig_adopt.update_layout(template="plotly_white")
            st.plotly_chart(fig_adopt, use_container_width=True)

        with col2:
            st.subheader("Product Mix Segmentation")
            latest_mix = product_mix.iloc[-1]
            mix_data = pd.DataFrame({
                "Segment": ["Insurance", "Investments", "Pure Mobile"],
                "Users": [latest_mix['insurance_subscribers'], latest_mix['investment_subscribers'], latest_mix['pure_mobile_users']]
            })
            fig_pie = px.pie(mix_data, names='Segment', values='Users', color_discrete_sequence=px.colors.sequential.Reds_r)
            st.plotly_chart(fig_pie, use_container_width=True)

        st.subheader("Cross-Sell Penetration Trends")
        fig_cross = go.Figure()
        fig_cross.add_trace(go.Scatter(x=cross_sell['period'], y=cross_sell['insurance_cross_sell_rate'], name="Insurance %", fill='tozeroy'))
        fig_cross.add_trace(go.Scatter(x=cross_sell['period'], y=cross_sell['investment_cross_sell_rate'], name="Investments %", fill='tonexty'))
        fig_cross.update_layout(template="plotly_white", yaxis_title="Penetration %")
        st.plotly_chart(fig_cross, use_container_width=True)

else:
    st.title("🌍 Pan-Africa Platform: Regional Consolidation")
    
    # Load Data via Portable Loader
    consolidation = load_data('SELECT * FROM mart_group_consolidation ORDER BY period', 'pan_africa_platform', 'mart_group_consolidation')
    comparison = load_data('SELECT * FROM mart_subsidiary_comparison ORDER BY period, profit_usd DESC', 'pan_africa_platform', 'mart_subsidiary_comparison')

    if not consolidation.empty:
        # Global Metrics
        latest_consol = consolidation.iloc[-1]
        g1, g2, g3 = st.columns(3)
        g1.metric("Consolidated Profit (USD)", f"${latest_consol['total_profit_usd']/1e6:.1f}M")
        g2.metric("Consolidated Profit (KES)", f"Sh{latest_consol['total_profit_kes']/1e9:.1f}B")
        g3.metric("Regional Footprint", f"{latest_consol['subsidiary_count']} Countries")

        st.markdown("---")

        st.subheader("Group-Level Profitability Trend (USD)")
        fig_group = px.area(consolidation, x='period', y='total_profit_usd', color_discrete_sequence=['#A60000'])
        fig_group.update_layout(template="plotly_white")
        st.plotly_chart(fig_group, use_container_width=True)

        col_a, col_b = st.columns(2)

        with col_a:
            st.subheader("Regional Profit Contribution (Latest Period)")
            latest_period = comparison['period'].iloc[-1]
            latest_comp = comparison[comparison['period'] == latest_period]
            fig_sub = px.bar(latest_comp, x='subsidiary', y='profit_usd', color='contribution_percentage', 
                             color_continuous_scale='Reds', text_auto='.2s')
            st.plotly_chart(fig_sub, use_container_width=True)

        with col_b:
            st.subheader("Regional Efficiency Comparison")
            st.dataframe(latest_comp[['subsidiary', 'contribution_percentage', 'profit_usd', 'profit_kes']], use_container_width=True)
