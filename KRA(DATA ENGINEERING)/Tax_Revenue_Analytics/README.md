# 🇰🇪 KRA Tax Revenue Analytics Warehouse

![Status](https://img.shields.io/badge/Status-Operational-green)
![Difficulty](https://img.shields.io/badge/Difficulty-Beginner-green)

## 📋 Overview
A data engineering platform designed to ingest and analyze Kenya Revenue Authority (KRA) tax collection reports. It tracks revenue performance across different tax heads (Income Tax, VAT, Excise, Customs) and compares actual collections against Treasury targets over a 15-year period.

## 🚀 Key Features
- **Automated KPI Extraction**: Standardizes tax head categories from historical reports (2009-2024).
- **Target vs. Actual Tracking**: Real-time monitoring of collection efficiency.
- **Historical Trend Analysis**: 15+ years of revenue data for fiscal policy research.
- **Interactive Dashboard**: Visualizes revenue breakdown and tax head efficiency.

## 🛠 Tech Stack
- **Ingestion**: Python (pdfplumber)
- **Warehouse**: PostgreSQL 15
- **Transformation**: dbt (Data Build Tool)
- **Orchestration**: Apache Airflow
- **Visualization**: Streamlit & Plotly

## 📊 Quick Start
1.  **Environment**: `cd KRA(DATA\ ENGINEERING)/Tax_Revenue_Analytics && docker compose up -d`
2.  **Dashboard**: `http://localhost:8506`
3.  **Airflow**: `http://localhost:8085`

---
*Developed by Victor Kipruto - KRA Data Engineering Portfolio*
