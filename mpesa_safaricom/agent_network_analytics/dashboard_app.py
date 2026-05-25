import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="M-Pesa Agent Analytics", layout="wide", page_icon="🗺️")

def load_agent_data():
    csv_path = "MPESA_Safaricom(pipeline)/Agent_Network_Analytics/data/agent_network_performance.csv"
    if not os.path.exists(csv_path):
        from ingestion.generate_agent_data import generate_agent_network_data
        generate_agent_network_data()
    return pd.read_csv(csv_path)

st.title("🗺️ M-Pesa Agent Network Geospatial Analytics")
st.markdown("Mapping agent density, transaction volumes, and liquidity across Kenya.")

df = load_agent_data()

# Summary Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Agents", len(df))
col2.metric("Total Monthly Volume", f"{df['monthly_txn_volume_kes'].sum()/1000000:,.1f}M KES")
col3.metric("Avg Agent Commission", f"{df['monthly_commission_kes'].mean():,.0f} KES")
col4.metric("Active Status %", f"{(df['status'] == 'Active').mean()*100:,.1f}%")

st.markdown("---")

tab1, tab2 = st.tabs(["Geospatial Map", "County Performance"])

with tab1:
    st.subheader("Agent Distribution & Volume (Heatmap)")
    # Filter by volume to reduce points for plotting
    fig_map = px.scatter_mapbox(df, lat="latitude", lon="longitude", color="monthly_txn_volume_kes", 
                                size="monthly_txn_volume_kes", hover_name="agent_id", 
                                mapbox_style="carto-positron", zoom=5, height=600)
    st.plotly_chart(fig_map, use_container_width=True)

with tab2:
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Volume by County")
        county_stats = df.groupby('county')['monthly_txn_volume_kes'].sum().reset_index()
        fig_bar = px.bar(county_stats.sort_values('monthly_txn_volume_kes'), x='county', y='monthly_txn_volume_kes', color='monthly_txn_volume_kes')
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col_b:
        st.subheader("Liquidity Risk (Low Float Agents)")
        # Agents with float < 10% of their volume
        low_float = df[df['current_float_kes'] < (df['monthly_txn_volume_kes'] * 0.05)]
        st.warning(f"Found {len(low_float)} agents with dangerously low float levels.")
        st.dataframe(low_float[['agent_id', 'county', 'current_float_kes', 'monthly_txn_volume_kes']].head(10), use_container_width=True)
