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
*   **Features**: HS code tracking, UN Comtrade integration.

### 3. [VAT Compliance & Gap Analysis](VAT_Compliance_Gap_Analysis/)
Fiscal policy modeling comparing theoretical VAT capacity vs. actual collections by sector.
*   **Methodology**: IMF VAT Gap framework.

### 4. [iTax Business Registration Analytics](iTax_Registration_Analytics/)
Scraping business registration data as an economic leading indicator.
*   **Tech Stack**: Playwright, PostGIS, dbt.

---

## 🛠 Portfolio Tech Stack
- **Ingestion**: Python (Requests, Playwright, pdfplumber)
- **Warehouse**: PostgreSQL 15 / DuckDB
- **Transformation**: dbt (Data Build Tool)
- **Orchestration**: Apache Airflow
- **Visualization**: Streamlit & Plotly

---
*Created by Victor Kipruto - Data Engineering Portfolio*
