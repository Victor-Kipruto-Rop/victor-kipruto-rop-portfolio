import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Page Config
st.set_page_config(page_title="Safaricom Integrated Analytics", layout="wide", page_icon="📱")

# Robust path handling for Streamlit Cloud
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_snapshot(snapshot_name):
    snapshot_path = os.path.join(BASE_DIR, "dashboards", "snapshots", f"{snapshot_name}.csv")
    if os.path.exists(snapshot_path):
        return pd.read_csv(snapshot_path)
    return pd.DataFrame()

st.title("📱 Safaricom PLC: Integrated Analytical Platform")
st.markdown("Consolidated monitoring of Financial Results, Credit Risk, Loyalty Systems, and Network Quality.")

# Navigation Tabs
tabs = st.tabs(["💰 Financial Results", "🛡️ Fuliza Credit Risk", "🎁 Bonga Loyalty", "📡 Network Quality"])

# Tab 1: Financial Results
with tabs[0]:
    st.subheader("Financial Performance Trends")
    fin_df = load_snapshot("mart_financial_results")
    seg_df = load_snapshot("mart_segment_revenue")
    
    if not fin_df.empty:
        latest = fin_df.iloc[-1]
        c1, c2, c3 = st.columns(3)
        c1.metric(f"Revenue ({latest['period']})", f"KES {latest['revenue_m_kes']/1000:,.1f}B")
        c2.metric("EBITDA", f"KES {latest['ebitda_m_kes']/1000:,.1f}B")
        c3.metric("Net Profit", f"KES {latest['net_profit_m_kes']/1000:,.1f}B")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            fig_fin = px.bar(fin_df, x='period', y=['revenue_m_kes', 'ebitda_m_kes', 'net_profit_m_kes'], 
                             barmode='group', title="Year-on-Year Growth (M KES)")
            st.plotly_chart(fig_fin, use_container_width=True)
            
        with col2:
            if not seg_df.empty:
                st.subheader("Revenue Mix (FY 2024)")
                fig_seg = px.pie(seg_df, names='segment', values='revenue_m_kes', hole=0.4,
                                 color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig_seg, use_container_width=True)
    else:
        st.warning("Financial data snapshots not found.")

# Tab 2: Fuliza Credit Risk
with tabs[1]:
    st.subheader("Fuliza Portfolio Quality & Performance")
    fuliza_df = load_snapshot("mart_fuliza_performance")
    
    if not fuliza_df.empty:
        latest_fuliza = fuliza_df.iloc[-1]
        c1, c2, c3 = st.columns(3)
        c1.metric("Monthly Disbursement", f"KES {latest_fuliza['amount_disbursed_m_kes']:,.1f}M")
        c2.metric("Active Monthly Users", f"{latest_fuliza['active_users_m']}M")
        c3.metric("NPL Ratio", f"{latest_fuliza['npl_ratio_percent']}%", delta_color="inverse")
        
        st.markdown("---")
        
        fig_disburse = px.line(fuliza_df, x='month', y='amount_disbursed_m_kes', title="Disbursement Trends (2025)", markers=True)
        st.plotly_chart(fig_disburse, use_container_width=True)
        
        fig_risk = px.area(fuliza_df, x='month', y='npl_ratio_percent', title="Portfolio Risk (NPL %) Evolution")
        st.plotly_chart(fig_risk, use_container_width=True)
    else:
        st.info("Fuliza risk analytics data unavailable.")

# Tab 3: Bonga Loyalty
with tabs[2]:
    st.subheader("Bonga Points Ecosystem")
    loyalty_df = load_snapshot("mart_bonga_loyalty")
    
    if not loyalty_df.empty:
        fig_loyalty = px.bar(loyalty_df, x='segment', y='active_loyalty_users', color='redemption_rate_percent',
                             text_auto=True, title="Active Loyalty Users by Segment & Redemption Rate")
        st.plotly_chart(fig_loyalty, use_container_width=True)
        
        st.write("### Redemption Efficiency Matrix")
        st.dataframe(loyalty_df.style.format({"total_points_m": "{:,.1f}", "redemption_rate_percent": "{:.1f}%", "active_loyalty_users": "{:,}"}), use_container_width=True)
    else:
        st.info("Loyalty analytics snapshots not found.")

# Tab 4: Network Quality
with tabs[3]:
    st.subheader("Regional Service Quality (Q1 2026)")
    net_df = load_snapshot("mart_network_quality")
    
    if not net_df.empty:
        c1, c2 = st.columns(2)
        with c1:
            fig_avail = px.bar(net_df.sort_values('availability_percent'), x='region', y='availability_percent', 
                               color='availability_percent', range_y=[99, 100], title="Network Availability (%)")
            st.plotly_chart(fig_avail, use_container_width=True)
        with c2:
            fig_speed = px.bar(net_df.sort_values('avg_speed_mbps'), x='region', y='avg_speed_mbps', 
                               color='avg_speed_mbps', color_continuous_scale='Turbo', title="Average Download Speed (Mbps)")
            st.plotly_chart(fig_speed, use_container_width=True)
            
        st.write("### CX Score Heatmap")
        fig_cx = px.scatter(net_df, x='latency_ms', y='avg_speed_mbps', size='cx_score', color='region', 
                           hover_name='region', title="Performance Matrix: Latency vs. Speed (Size = CX Score)")
        st.plotly_chart(fig_cx, use_container_width=True)
    else:
        st.info("Network quality data snapshots not found.")

# Sidebar
st.sidebar.title("Data Controls")
if st.sidebar.button("Refresh Data Snapshots"):
    st.rerun()

st.sidebar.markdown("""
**Data Sources:**
- Safaricom FY 2024/25 Results
- Investor Relations IR Data
- GSMA Mobile Money Reports
- Network Performance Monitoring Logs
""")

st.sidebar.info("Dashboard integrates Financial Results, Fuliza Risk, Bonga Loyalty, and Network Quality projects.")
