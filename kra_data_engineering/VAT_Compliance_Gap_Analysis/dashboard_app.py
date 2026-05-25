import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import os

st.set_page_config(page_title="KRA: VAT Compliance Analytics", layout="wide", page_icon="📉")

def load_data(query, snapshot_name):
    try:
        if os.path.exists("/.dockerenv"):
            host = "postgres-kra"
            port = "5432"
        else:
            host = "localhost"
            port = "5438"
            
        engine = create_engine(f'postgresql://kra_admin:kra_password@{host}:{port}/kra_warehouse')
        return pd.read_sql(query, engine)
    except Exception as e:
        st.sidebar.warning(f"Live DB connection failed: {e}. Using snapshots.")
        snapshot_path = f"dashboards/snapshots/{snapshot_name}.csv"
        if os.path.exists(snapshot_path):
            return pd.read_csv(snapshot_path)
        return pd.DataFrame()

st.title("📉 KRA: VAT Compliance & Gap Analysis")
st.markdown("Sector-level analysis of VAT collection efficiency and theoretical vs. actual revenue.")

df = load_data("SELECT * FROM mart_vat_gap_by_sector ORDER BY year DESC, vat_gap_m_kes DESC", "mart_vat_gap_by_sector")

if not df.empty:
    latest_year = df['year'].max()
    latest_data = df[df['year'] == latest_year]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total VAT Gap (B KES)", f"{latest_data['vat_gap_m_kes'].sum()/1000:,.1f}B")
    col2.metric("Overall C-Efficiency", f"{(latest_data['actual_vat_m_kes'].sum() / latest_data['theoretical_vat_m_kes'].sum() * 100):,.1f}%")
    col3.metric("Highest Gap Sector", latest_data.nlargest(1, 'vat_gap_m_kes')['sector'].iloc[0])

    st.markdown("---")
    
    tab1, tab2 = st.tabs(["Compliance Gap", "Sector Efficiency"])
    
    with tab1:
        st.subheader("Theoretical vs Actual VAT by Sector")
        fig_gap = px.bar(latest_data, x='sector', y=['actual_vat_m_kes', 'vat_gap_m_kes'], 
                         title="VAT Revenue Potential", barmode='stack')
        st.plotly_chart(fig_gap, use_container_width=True)
        
    with tab2:
        st.subheader("Sectoral C-Efficiency Trends")
        fig_trend = px.line(df, x='year', y='c_efficiency_ratio', color='sector', markers=True)
        fig_trend.add_hline(y=1.0, line_dash="dot", line_color="green", annotation_text="Perfect Compliance")
        st.plotly_chart(fig_trend, use_container_width=True)

else:
    st.warning("No data found. Ensure the ETL pipeline has run successfully.")
