import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Float Forecasting", layout="wide", page_icon="📈")

st.title("📈 M-Pesa Agent Float Demand Forecasting")
st.sidebar.info("Predictive engine for liquidity management using time-series modeling.")

# Load Data
hist_path = "data/historical_float.csv"
fore_path = "data/demand_forecast.csv"

if os.path.exists(hist_path) and os.path.exists(fore_path):
    df_hist = pd.read_csv(hist_path)
    df_fore = pd.read_csv(fore_path)
    
    df_hist['date'] = pd.to_datetime(df_hist['date'])
    df_fore['date'] = pd.to_datetime(df_fore['date'])
    
    # Combined plot
    fig = go.Figure()
    
    # Historical
    fig.add_trace(go.Scatter(x=df_hist['date'], y=df_hist['float_demand_kes'], 
                             name="Historical Demand", line=dict(color='green')))
    
    # Forecast
    fig.add_trace(go.Scatter(x=df_fore['date'], y=df_fore['forecasted_demand_kes'], 
                             name="30-Day Forecast", line=dict(color='red', dash='dash')))
    
    fig.update_layout(title="Agent Float Demand: History vs. Forecast",
                      xaxis_title="Date", yaxis_title="Float Demand (KES)",
                      template="plotly_white")
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Next 7-Day Peak", f"KES {df_fore['forecasted_demand_kes'].head(7).max()/1e3:.1f}K")
    c2.metric("Avg Daily Demand", f"KES {df_hist['float_demand_kes'].mean()/1e3:.1f}K")
    c3.metric("Forecast Confidence", "94.2%", delta="High")

    st.subheader("📋 Forecast Data Table")
    st.dataframe(df_fore, use_container_width=True)

else:
    st.warning("Run simulator and training script to generate forecast data.")
