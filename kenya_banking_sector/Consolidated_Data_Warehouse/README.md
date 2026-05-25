# 🏦 Kenya Banking Sector Consolidated Data Warehouse

![Status](https://img.shields.io/badge/Status-Operational-green)
![Data](https://img.shields.io/badge/Source-CBK_Reports-blue)

## 📋 Overview
The central "Source of Truth" for the Kenyan banking industry. This project automates the ingestion of CBK Bank Supervision Annual Reports (2015-2025) into a robust, star-schema PostgreSQL warehouse, enabling cross-bank benchmarking and sector-wide trend analysis.

## 🚀 Key Features
- **Automated KPI Extraction**: Parses technical CBK Return Codes into human-readable metrics (ROE, ROA, NIM, NPL).
- **Star Schema Design**: Optimized for high-performance analytical queries.
- **Peer Benchmarking**: Compare Tier 1 banks (KCB, Equity, Absa) against the broader sector.
- **Data Reconciliation**: Built-in logic to bridge gaps between different reporting formats.

## Data Sources
- **Central Bank of Kenya (CBK)**: Annual Bank Supervision Reports (10+ years).
- **Institution Disclosures**: Audited financial results from individual commercial banks.

## 🛠 Tech Stack
- **Transformation**: dbt (Data Build Tool)
- **Database**: PostgreSQL 15
- **Orchestration**: Apache Airflow
- **Visualization**: Streamlit

## 📊 Key Metrics Tracked
- **Total Sector Assets**: Aggregated growth of the Kenyan banking industry.
- **Asset Quality**: NPL Ratio trends across tiers.
- **Market Share**: Distribution of deposits and loans by institution.

## 📂 Project Structure
```bash
Consolidated_Data_Warehouse/
├── dags/               # Airflow ETL schedules
├── dbt/                # Transformation logic & models
├── ingestion/          # Extraction scripts (PDF -> DB)
├── seeds/              # Reference data (Bank Registry)
└── dashboard_app.py    # Consolidated analytics view
```

---
*Developed as part of the Kenya Banking Sector Analytics Portfolio*
