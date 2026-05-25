# 🏦 Equity Group Integrated Data Platform

![Project Architecture](./images/_285059c4-f803-462b-9a02-95b214d40f97.jpeg)

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

- **Live Demo**: [🚀 Click Here to Open Dashboard](https://kipruto45-victor-kipruto-rop-portfolio-g8pspygfpttsbfggjaadwy.streamlit.app/)
- **Local Access**: `http://localhost:8502`
- **How to Use**:
    1. **Regional Comparison**: Use the "Pan-Africa Consolidation" mode to see how subsidiaries in DRC, Rwanda, and Uganda compare in USD profit.
    2. **Risk Analysis**: Switch to the **Regional Engagement & Risk** tab to see bubble charts of Digital Maturity vs. Credit Risk.
    3. **Growth Tracking**: Use the "Equitel & EazzyPay" mode to track subscriber S-curves and transaction velocity.
- **Portability**: This dashboard uses a "Portable Mode" fallback—if the live PostgreSQL database is not available, it automatically loads pre-processed data snapshots for instant viewing.

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

## 🚀 Project Goals
The platform provides a unified view of Equity Group's Pan-African operations, handling complex multi-currency normalization across 7 subsidiaries and modeling digital adoption.

---
*Maintained by the Data Engineering Team*


## Data Sources

This project utilizes the following data sources:
- `Equitel_EazzyPay_Analytics/ingestion/eazzypay_transactions.csv`
- `Equitel_EazzyPay_Analytics/ingestion/equitel_subscribers.csv`
- `Pan_Africa_Financial_Platform/dbt/seeds/customer_master.csv`
- `Pan_Africa_Financial_Platform/dbt/seeds/subsidiaries.csv`
- `Pan_Africa_Financial_Platform/dbt/target/run/pan_africa_platform/seeds/customer_master.csv`
- `Pan_Africa_Financial_Platform/dbt/target/run/pan_africa_platform/seeds/subsidiaries.csv`
- `Pan_Africa_Financial_Platform/ingestion/equity_subsidiary_performance.csv`
- `Pan_Africa_Financial_Platform/ingestion/subsidiary_financials.csv`
- `dashboards/snapshots/mart_adoption_curve.csv`
- `dashboards/snapshots/mart_arpu_benchmark.csv`
- `dashboards/snapshots/mart_cross_sell_rate.csv`
- `dashboards/snapshots/mart_group_consolidation.csv`
- `dashboards/snapshots/mart_product_mix.csv`
- `dashboards/snapshots/mart_regional_engagement.csv`
- `dashboards/snapshots/mart_subsidiary_comparison.csv`
- `dashboards/snapshots/mart_subsidiary_performance.csv`
