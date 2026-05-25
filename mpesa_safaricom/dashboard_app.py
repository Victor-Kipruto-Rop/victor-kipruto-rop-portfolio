import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="M-Pesa Safaricom Pipeline", layout="wide", page_icon="🟢")

st.title("🟢 M-Pesa Safaricom Pipeline Dashboard")
st.markdown("Centralized overview of real-time transactions, fraud detection, and agent networks.")

st.info("Select a specific sub-project from the sidebar to view detailed analytics.")

st.sidebar.title("Navigation")
projects = [d for d in os.listdir('.') if os.path.isdir(d) and not d.startswith('.')]
selected_project = st.sidebar.selectbox("Select Project", projects)

st.write(f"### Currently viewing: {selected_project}")
st.write("To view the detailed dashboard for this project, run its specific `dashboard_app.py` if available.")
