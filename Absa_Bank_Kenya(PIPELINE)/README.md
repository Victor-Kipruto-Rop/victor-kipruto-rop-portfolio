# 🏦 Absa Bank Kenya Integrated Data Platform

![Project Architecture](./images/absa.png)

This directory contains the integrated data engineering pipelines for Absa Bank Kenya, consolidating financial performance tracking and open banking innovation into a single, unified infrastructure.

## 🚀 Overview

The platform is designed to provide end-to-end visibility into Absa's operational and customer health. It transitions from traditional report parsing (KPI Warehouse) to modern, real-time API integrations (Open Banking), all orchestrated via a shared Airflow and PostgreSQL environment.

## 🛠️ Integrated Projects

| Project Name | Tech Stack | Description |
| :--- | :--- | :--- |
| [Financial KPIs Warehouse](./Financial_KPIs_Warehouse) | `Python`, `dbt`, `PostgreSQL`, `Airflow`, `Metabase`, `pdfplumber` | Automated extraction of financial metrics from annual reports and NSE filings (2020-Present). |
| [Open Banking API Pipeline](./Open_Banking_API_Pipeline) | `Python`, `FastAPI`, `dbt`, `PostgreSQL`, `Airflow`, `Pydantic` | Consent-driven transaction ingestion with automated cash-flow credit scoring logic. |

## 🏗️ Unified Infrastructure

The projects share a common containerized environment managed at this root level:

- **Shared Database**: PostgreSQL instance with dual-database initialization (`absa_warehouse` and `absa_open_banking`).
- **Unified Orchestrator**: A single Apache Airflow instance managing DAGs for both pipelines.
- **BI Layer**: Metabase for cross-project data visualization.
- **API Layer**: FastAPI service exposing open banking data products.

## 📊 Integrated Analytics Dashboard

The platform includes a comprehensive Streamlit dashboard providing real-time visibility into both financial health and digital adoption.

### Key Features:
- **💰 Financial KPIs**: Real-time tracking of Net Profit, ROE, and Cost-to-Income ratios based on the latest 2025 audited results.
- **🛡️ Risk & Capital**: Visualization of Asset Quality (NPL ratios) and Capital Adequacy (CAR) relative to statutory minimums.
- **🔌 Open Banking Insights**: Monitoring of API transaction volumes and customer activity trends from the Open Banking API pipeline.

### Accessing the Dashboards:
1. **Interactive Dashboard (Streamlit)**: 
   - **Live Demo**: [🚀 View Live Dashboard](https://kipruto45-victor-kipruto-rop-portfolio-cc6ye8wlqrt2vtpsdndigd.streamlit.app/)
   - **Local URL**: [http://localhost:8501](http://localhost:8501)
   - **Command**: `streamlit run dashboard_app.py` from the project root.
2. **BI Layer (Metabase)**:
   - **URL**: [http://localhost:3000](http://localhost:3000)
   - Pre-defined SQL queries are available in the `dashboards/` directory.
3. **Master Hub**: Accessible via the [Master Dashboard](../master_dashboard.py).

## 🚦 Getting Started

### 1. Environment Setup
Create a `.env` file in this directory based on `.env.example` with your Absa Developer credentials:
```env
ABSA_CONSUMER_KEY=your_key
ABSA_CONSUMER_SECRET=your_secret
```

### 2. Verify API Connection
You can test your Playpen credentials by running the automated connection test:
```bash
python3 Open_Banking_API_Pipeline/test_api_connection.py
```
This script will authenticate against `https://www.api.absa.africa:9443` and attempt to list accounts.

### 3. Launch Services
Use the unified Makefile to start the platform:
```bash
make up
```

### 3. Run Pipelines
Execute end-to-end data flows for both projects:
```bash
# KPI Warehouse
make dbt-seed-kpi
make dbt-run-kpi

# Open Banking
make dbt-run-api
```

## 🚀 Project Goals
The platform is designed to provide end-to-end visibility into Absa's operational and customer health, transitioning from traditional report parsing to modern real-time API integrations.

---
*Maintained by the Data Engineering Team*


## Data Sources

This project utilizes the following data sources:
- `2025-integrated-annual-report.pdf`
- `Absa-Group-Limited-Integrated-Report.pdf`
- `Absa-Group-Pillar-3-disclosure-as-at-31-December-2025.pdf`
- `Financial_KPIs_Warehouse/ingestion/absa_robust_financials.csv`
- `Financial_KPIs_Warehouse/ingestion/raw_absa_historical.csv`
- `Financial_KPIs_Warehouse/seeds/kpi_definitions.csv`
- `Open_Banking_API_Pipeline/seeds/customer_consent.csv`
- `dashboards/snapshots/mart_asset_quality.csv`
- `dashboards/snapshots/mart_customer_activity.csv`
- `dashboards/snapshots/mart_efficiency_ratio.csv`
- `dashboards/snapshots/mart_profitability.csv`
- `dashboards/snapshots/raw_transactions.csv`
