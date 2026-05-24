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

## 📊 Dashboards

The platform includes two ways to visualize insights:

### 1. Modern Interactive Dashboards (Streamlit)
A high-fidelity, interactive dashboard built with Streamlit and Plotly.
- **Access**: `http://localhost:8501`
- **Features**: Interactive time-series trends, NPL ratio analysis, and account distribution charts.

### 2. BI Layer (Metabase)
Pre-defined SQL queries for Metabase dashboards in the `dashboards/` directory.
- **Access**: `http://localhost:3000`

## 🚦 Getting Started

### 1. Environment Setup
Create a `.env` file in this directory with your Absa Developer credentials:
```env
ABSA_CONSUMER_KEY=your_key
ABSA_CONSUMER_SECRET=your_secret
```

### 2. Launch Services
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

## 📊 Analytical Deliverables
Detailed insights are available in the executed Jupyter notebooks within each project's `notebooks/` directory:
- **Rebranding Analysis**: Impact of the Barclays-to-Absa transition on key metrics.
- **Credit Scoring Model**: Cash-flow based creditworthiness evaluation engine.

---
*Maintained by the Data Engineering Team*
