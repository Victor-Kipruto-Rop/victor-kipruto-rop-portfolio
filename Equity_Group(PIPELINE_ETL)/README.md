# 🏦 Equity Group Integrated Data Platform

This directory contains the integrated data engineering pipelines for Equity Group, covering multi-national financial consolidation and mobile banking (Equitel/EazzyPay) analytics.

## 🚀 Overview

The platform provides a unified view of Equity Group's Pan-African operations. It handles complex multi-currency normalization across 7 subsidiaries and models adoption curves for its MVNO and digital payment platforms, all managed via a shared infrastructure.

## 🛠️ Integrated Projects

| Project Name | Tech Stack | Description |
| :--- | :--- | :--- |
| [Equitel & EazzyPay Analytics](./Equitel_EazzyPay_Analytics) | `Python`, `dbt`, `PostgreSQL`, `Airflow`, `Matplotlib` | Analysis of mobile banking adoption, transaction velocity, and ARPU trends. |
| [Pan-Africa Financial Platform](./Pan_Africa_Financial_Platform) | `Python`, `dbt`, `PostgreSQL`, `Airflow`, `Forex Logic` | Multi-subsidiary financial consolidation with automated currency normalization to USD and KES. |

## 🏗️ Unified Infrastructure

The projects share a common containerized environment managed at this root level:

- **Shared Database**: PostgreSQL instance with dual-database initialization (`equitel_analytics` and `pan_africa_platform`).
- **Unified Orchestrator**: A single Apache Airflow instance managing DAGs for both regional consolidation and mobile analytics.
- **BI & Visualization**: Integrated Metabase for dashboarding and embedded Matplotlib visuals in executed notebooks.

## 📊 Dashboards

The platform includes two ways to visualize insights:

### 1. Modern Interactive Dashboards (Streamlit)
A high-fidelity, interactive dashboard built with Streamlit and Plotly.
- **Access**: `http://localhost:8502`
- **Features**: Regional profit contribution maps, adoption S-curves, and product cross-sell penetration.

### 2. BI Layer (Metabase)
Pre-defined SQL queries for Metabase dashboards in the `dashboards/` directory.
- **Access**: `http://localhost:3001`

## 🚦 Getting Started

### 1. Launch Services
Use the unified Makefile to start the platform:
```bash
make up
```

### 2. Run Pipelines
Execute end-to-end data flows for both projects:
```bash
# Equitel Analytics
make dbt-run-equitel

# Pan-Africa Platform
make dbt-run-pan-africa
```

## 📊 Analytical Deliverables
Detailed insights are available in the executed Jupyter notebooks:
- **Adoption Analysis**: [View Notebook](./Equitel_EazzyPay_Analytics/notebooks/adoption_analysis.ipynb) - EazzyPay velocity and ARPU trends.
- **Consolidation Analysis**: [View Notebook](./Pan_Africa_Financial_Platform/notebooks/consolidation_analysis.ipynb) - Group-level USD profit contribution by subsidiary.

---
*Maintained by the Data Engineering Team*
