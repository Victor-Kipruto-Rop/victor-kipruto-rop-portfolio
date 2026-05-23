import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
import os

# Page Config
st.set_page_config(page_title="Absa Kenya Financial Insights", layout="wide", page_icon="🏦")

# Data Loader (Postgres with CSV Fallback)
def load_data(query, db_name, snapshot_name):
    try:
        # Try local DB first (Docker environment)
        # Using 127.0.0.1 for local, 'postgres' for inside docker
        host = "postgres" if os.path.exists("/.dockerenv") else "localhost"
        engine = create_engine(f'postgresql://absa_admin:absa_password@{host}:5432/{db_name}')
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
st.sidebar.title("Absa Integrated Platform")
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Absa_Group_Logo.svg/1024px-Absa_Group_Logo.svg.png", width=150)
app_mode = st.sidebar.selectbox("Choose Dashboard", ["Financial KPIs", "Open Banking Analytics"])

if app_mode == "Financial KPIs":
    st.title("📊 Absa Kenya: Financial KPIs Warehouse")
    
    # Load Data via Portable Loader
    profitability = load_data('SELECT * FROM mart_profitability ORDER BY period', 'absa_warehouse', 'mart_profitability')
    asset_quality = load_data('SELECT * FROM mart_asset_quality ORDER BY period', 'absa_warehouse', 'mart_asset_quality')
    efficiency = load_data('SELECT * FROM mart_efficiency_ratio ORDER BY period', 'absa_warehouse', 'mart_efficiency_ratio')

    if not profitability.empty:
        # Key Metrics
        m1, m2, m3, m4 = st.columns(4)
        latest_roe = profitability['roe_percentage'].iloc[-1]
        latest_npl = asset_quality['npl_ratio_percentage'].iloc[-1]
        latest_nim = profitability['nim_percentage'].iloc[-1]
        latest_cir = efficiency['cost_to_income_ratio'].iloc[-1]

        m1.metric("Latest ROE", f"{latest_roe:.2f}%", delta=f"{latest_roe - profitability['roe_percentage'].iloc[-2]:.2f}%")
        m2.metric("NPL Ratio", f"{latest_npl:.2f}%", delta=f"{latest_npl - asset_quality['npl_ratio_percentage'].iloc[-2]:.2f}%", delta_color="inverse")
        m3.metric("Net Interest Margin", f"{latest_nim:.2f}%")
        m4.metric("Cost to Income", f"{latest_cir:.2f}%")

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Profitability Trends")
            fig_prof = go.Figure()
            fig_prof.add_trace(go.Scatter(x=profitability['period'], y=profitability['roe_percentage'], name="ROE %", line=dict(color='red', width=3)))
            fig_prof.add_trace(go.Scatter(x=profitability['period'], y=profitability['nim_percentage'], name="NIM %", line=dict(color='blue', dash='dash')))
            fig_prof.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_prof, use_container_width=True)

        with col2:
            st.subheader("Asset Quality (NPL Amount vs Ratio)")
            fig_npl = px.bar(asset_quality, x='period', y='npl_amount', text_auto='.2s', color_discrete_sequence=['#A60000'])
            fig_npl.add_trace(go.Scatter(x=asset_quality['period'], y=asset_quality['npl_ratio_percentage'], name="NPL %", yaxis="y2"))
            fig_npl.update_layout(
                yaxis2=dict(title="NPL %", overlaying="y", side="right"),
                template="plotly_white",
                showlegend=False
            )
            st.plotly_chart(fig_npl, use_container_width=True)

        st.subheader("Operational Efficiency (Cost-to-Income)")
        fig_cir = px.area(efficiency, x='period', y='cost_to_income_ratio', color_discrete_sequence=['gray'])
        fig_cir.add_hline(y=50, line_dash="dot", line_color="red", annotation_text="Target")
        st.plotly_chart(fig_cir, use_container_width=True)

else:
    st.title("🔓 Absa Open Banking: Transaction Intelligence")
    
    # Load Data via Portable Loader
    activity = load_data('SELECT * FROM mart_customer_activity ORDER BY activity_date', 'absa_open_banking', 'mart_customer_activity')
    raw_txns = load_data('SELECT * FROM raw_transactions', 'absa_open_banking', 'raw_transactions')

    if not raw_txns.empty:
        # Metrics
        t1, t2, t3 = st.columns(3)
        t1.metric("Total Synced Txns", len(raw_txns))
        t2.metric("Total Volume (KES)", f"{raw_txns['amount'].sum():,.2f}")
        t3.metric("Unique Accounts", raw_txns['account_id'].nunique())

        st.markdown("---")

        st.subheader("Daily Transaction Volume")
        fig_vol = px.line(activity, x='activity_date', y='total_volume', markers=True, color_discrete_sequence=['#D10000'])
        fig_vol.update_layout(template="plotly_white")
        st.plotly_chart(fig_vol, use_container_width=True)

        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("Account Activity Distribution")
            fig_acc = px.pie(raw_txns, names='account_id', values='amount', hole=0.4)
            st.plotly_chart(fig_acc, use_container_width=True)
        
        with c2:
            st.subheader("Latest Transactions")
            st.dataframe(raw_txns.sort_values('transaction_date', ascending=False).head(10), use_container_width=True)
