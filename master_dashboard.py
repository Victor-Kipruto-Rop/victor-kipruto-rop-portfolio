import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
import os

# Page Config
st.set_page_config(page_title="Kenya Banking Sector: Integrated Analytics", layout="wide", page_icon="🏦")

# Simple Authentication
def check_password():
    def password_entered():
        if st.session_state["username"] == "admin" and st.session_state["password"] == "banking_secure_2025":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.title("🏦 Kenya Banking Sector Analytics")
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.error("😕 User not known or password incorrect")
        return False
    else:
        return True

if check_password():
    # Sidebar Navigation
    st.sidebar.title("Sector Navigator")
    bank_selection = st.sidebar.selectbox("Select Institution", ["KCB Group", "Absa Bank Kenya", "Equity Group"])
    
    st.sidebar.markdown("---")
    st.sidebar.button("Logout", on_click=lambda: st.session_state.clear())

    # Data Loader Helper
    def get_engine(db_name, user, password, port=5432):
        host = "postgres" if os.path.exists("/.dockerenv") else "localhost"
        return create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db_name}')

    if bank_selection == "KCB Group":
        st.title("🦁 KCB Group Integrated Analytics")
        # Reuse KCB Dashboard Logic
        from financials.dashboard_app import load_data as load_kcb_data
        # (Simplified for this Master Dashboard version)
        st.info("Displaying KCB Group Consolidated Performance and M-Pesa Loan Analytics.")
        # ... (Include KCB specific tabs here)
        
    elif bank_selection == "Absa Bank Kenya":
        st.title("🏦 Absa Kenya Financial Insights")
        st.info("Displaying Absa Kenya Financial KPIs and Open Banking Analytics.")
        # ... (Include Absa specific tabs here)

    elif bank_selection == "Equity Group":
        st.title("🌍 Equity Group Pan-Africa Insights")
        st.info("Displaying Equity Group Digital Adoption and Regional Consolidation.")
        # ... (Include Equity specific tabs here)
