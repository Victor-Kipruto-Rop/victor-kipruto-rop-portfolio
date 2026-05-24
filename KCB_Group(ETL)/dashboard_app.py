import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
import os

# Simple Authentication
def check_password():
    """Returns True if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] == "admin" and st.session_state["password"] == "kcb_secure_2025":
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show inputs for username and password.
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 User not known or password incorrect")
        return False
    else:
        # Password correct.
        return True

# Page Config
st.set_page_config(page_title="KCB Group Financial & Loan Analytics", layout="wide", page_icon="🦁")

if check_password():
    # Data Loader (Postgres with CSV Fallback)
    def load_data(query, db_name, snapshot_name, project_name):
        try:
            host = "postgres" if os.path.exists("/.dockerenv") else "localhost"
            engine = create_engine(f'postgresql://kcb_admin:kcb_password@{host}:5436/{db_name}')
            return pd.read_sql(query, engine)
        except Exception:
            # Fallback to snapshots
            base_path = os.path.dirname(__file__)
            snapshot_path = os.path.join(base_path, project_name, "dashboards", "snapshots", f"{snapshot_name}.csv")
            if os.path.exists(snapshot_path):
                return pd.read_csv(snapshot_path)
            else:
                return pd.DataFrame()

    # Sidebar
    st.sidebar.title("KCB Group Integrated Platform")
    st.sidebar.markdown("### 🦁 KCB Bank Group")
    st.sidebar.button("Logout", on_click=lambda: st.session_state.clear())
    app_mode = st.sidebar.selectbox("Choose Dashboard", ["Subsidiary Performance", "M-Pesa Loan Book (Vintage Analysis)"])

    if app_mode == "Subsidiary Performance":
        st.title("📊 KCB Group: Regional Subsidiary Performance")
        
        performance = load_data('SELECT * FROM mart_subsidiary_performance ORDER BY year', 'kcb_financials', 'mart_subsidiary_performance', 'Financial_Performance_Tracker')
        nim_data = load_data('SELECT * FROM mart_nim_trend ORDER BY year', 'kcb_financials', 'mart_nim_trend', 'Financial_Performance_Tracker')
        profitability = load_data('SELECT * FROM mart_roe_roa ORDER BY year', 'kcb_financials', 'mart_roe_roa', 'Financial_Performance_Tracker')

        if not performance.empty:
            # Latest Year Summary
            latest_year = performance['year'].max()
            latest_data = performance[performance['year'] == latest_year]
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Group Profit (M KES)", f"{latest_data['net_profit_m_kes'].sum():,.2f}")
            c2.metric("Total Group Assets (B KES)", f"{latest_data['total_assets_m_kes'].sum()/1000:,.2f}")
            c3.metric("Avg Group NPL %", f"{latest_data['npl_ratio_percent'].mean():,.2f}%")
            
            avg_roe = profitability[profitability['year'] == latest_year]['roe_percent'].mean() if not profitability.empty else 0
            c4.metric("Avg Group ROE %", f"{avg_roe:,.2f}%")

            st.markdown("---")

            tab1, tab2, tab3 = st.tabs(["Profit & Assets", "KPI Trends (NIM/ROE)", "Efficiency & Risk"])

            with tab1:
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Profit Contribution by Subsidiary")
                    fig_profit = px.pie(latest_data, names='subsidiary', values='net_profit_m_kes', hole=0.4, color_discrete_sequence=px.colors.sequential.Reds_r)
                    st.plotly_chart(fig_profit, use_container_width=True)
                    
                with col2:
                    st.subheader("Asset Quality (NPL Ratio) per Market")
                    fig_npl = px.bar(latest_data.sort_values('npl_ratio_percent'), x='subsidiary', y='npl_ratio_percent', color='npl_ratio_percent', color_continuous_scale='Reds')
                    st.plotly_chart(fig_npl, use_container_width=True)

                st.subheader("Regional Profit Growth Trends")
                fig_trend = px.line(performance, x='year', y='net_profit_m_kes', color='subsidiary', markers=True)
                fig_trend.update_layout(template="plotly_white")
                st.plotly_chart(fig_trend, use_container_width=True)

            with tab2:
                st.subheader("Net Interest Margin (NIM) Trends")
                if not nim_data.empty:
                    fig_nim = px.line(nim_data, x='year', y='nim_percent', color='subsidiary', markers=True, title="NIM % by Subsidiary")
                    st.plotly_chart(fig_nim, use_container_width=True)
                
                st.subheader("Return on Equity (ROE) Performance")
                if not profitability.empty:
                    fig_roe = px.bar(profitability[profitability['year'] == latest_year], x='subsidiary', y='roe_percent', color='roe_percent', title=f"ROE % in {latest_year}")
                    st.plotly_chart(fig_roe, use_container_width=True)

            with tab3:
                st.subheader("Cost-to-Income Efficiency")
                # Assuming mart_subsidiary_perf contains cost_to_income_ratio
                eff_data = load_data('SELECT * FROM mart_subsidiary_perf', 'kcb_financials', 'mart_subsidiary_perf', 'Financial_Performance_Tracker')
                if not eff_data.empty:
                    latest_eff = eff_data[eff_data['year'] == latest_year]
                    fig_eff = px.scatter(latest_eff, x='net_profit_m_kes', y='cost_to_income_ratio', size='customer_count', color='subsidiary', 
                                         title="Profitability vs. Efficiency (Bubble size = Customers)")
                    st.plotly_chart(fig_eff, use_container_width=True)

    else:
        st.title("📱 KCB M-Pesa: Mobile Loan Book Analytics")
        
        vintage = load_data('SELECT * FROM mart_vintage_analysis ORDER BY cohort_month, month_offset', 'kcb_mpesa', 'mart_vintage_analysis', 'MPesa_Loan_Book_Analytics')

        if not vintage.empty:
            st.subheader("Vintage Analysis: Default Rates by Cohort")
            # Pivot for heatmap style or multiple lines
            fig_vint = px.line(vintage, x='month_offset', y='default_rate_percent', color='cohort_month', 
                               title="Default Rate Evolution by Disbursement Cohort", labels={'month_offset': 'Months Since Disbursement'})
            fig_vint.update_layout(template="plotly_white")
            st.plotly_chart(fig_vint, use_container_width=True)

            col_a, col_b = st.columns(2)
            with col_a:
                st.subheader("Repayment Velocity")
                fig_repay = px.line(vintage, x='month_offset', y='repayment_rate_percent', color='cohort_month')
                st.plotly_chart(fig_repay, use_container_width=True)
            with col_b:
                st.subheader("Cohort Risk Profile (at Month 6)")
                m6_data = vintage[vintage['month_offset'] == 6]
                fig_risk = px.scatter(m6_data, x='amount_disbursed_m_kes', y='default_rate_percent', size='amount_disbursed_m_kes', color='cohort_month', 
                                      title="Volume vs Default Risk (Month 6)")
                st.plotly_chart(fig_risk, use_container_width=True)
