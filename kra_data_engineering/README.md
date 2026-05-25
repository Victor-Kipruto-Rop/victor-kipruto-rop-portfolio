# 🇰🇪 KRA Data Engineering & Analytics Portfolio

## Overview
This repository contains a suite of data engineering projects designed to automate the ingestion, transformation, and analysis of Kenya Revenue Authority (KRA) data. The portfolio covers national tax revenue analytics, customs and trade monitoring, and business registration trends.

---

## 🚀 Key Projects

### 1. [Tax Revenue Analytics Warehouse](Tax_Revenue_Analytics/)
Automated ingestion of KRA monthly revenue performance reports to track collection efficiency against Treasury targets.
*   **Tech Stack**: Python (pdfplumber), dbt, Airflow, PostgreSQL.
*   **Dashboard**: `http://localhost:8506`

### 2. [Customs & Trade Data Pipeline](Customs_Trade_Pipeline/)
Import/export intelligence tracking commodity-level trade volumes, duty collection, and contraband risk scoring.
*   **Data Sources**: Real-world integration of **FY 2020/21 Audited Revenue Reports**, **UN Comtrade** international trade benchmarks, and **Rules of Origin** regulatory disclosures.

### 3. [VAT Compliance & Gap Analysis](VAT_Compliance_Gap_Analysis/)
Fiscal policy modeling comparing theoretical VAT capacity vs. actual collections by sector.
*   **Methodology**: IMF VAT Gap framework.

### 4. [iTax Business Registration Analytics](iTax_Registration_Analytics/)
Scraping business registration data as an economic leading indicator.
*   **Tech Stack**: Playwright, PostGIS, dbt.

## 📊 Integrated Analytics Dashboard

The platform includes a centralized Streamlit hub that provides deep-dive insights into national revenue and trade performance.

### Key Features:
- **📈 Tax Revenue Performance**: Monitoring of collections vs. Treasury targets (e.g., VAT, PAYE, Excise).
- **🚢 Customs & Trade Intelligence**: Analysis of trade volumes (Tons), trade value (KES), and HS-code duty contribution.
- **📉 Macro-Economic Indicators**: Heatmaps of industry growth rates from the 2026 Economic Survey and Tax-to-GDP efficiency modeling.

### Accessing the Dashboards:
1. **Interactive Dashboard (Streamlit)**: 
   - **Live Demo**: [🚀 View KRA Integrated Dashboard](https://kipruto45-victor-kipruto-rop-portfolio-g8pspygfpttsbfggjaadwy.streamlit.app/)
   - **Local URL**: [http://localhost:8506](http://localhost:8506)
   - **Command**: `streamlit run dashboard_app.py` from the project root.
2. **Master Hub**: Accessible via the [Master Dashboard](../master_dashboard.py).


## 🛠 Portfolio Tech Stack
- **Ingestion**: Python (Requests, Playwright, pdfplumber)
- **Warehouse**: PostgreSQL 15 / DuckDB
- **Transformation**: dbt (Data Build Tool)
- **Orchestration**: Apache Airflow
- **Visualization**: Streamlit & Plotly

---
*Created by Victor Kipruto - Data Engineering Portfolio*
