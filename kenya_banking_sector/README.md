![Kenya Banking Sector Banner](image.png)

# 🏦 Kenya Banking Sector: Integrated Data Engineering Portfolio

## Overview
This repository contains a suite of advanced data engineering and analytics platforms focused on the Kenyan Banking Sector. It provides a macro-level view of the entire industry (38+ banks) while deep-diving into specific domains like AML compliance, regional peer analysis, and digital banking adoption.

---

## 🚀 Key Projects

### 1. [Consolidated Data Warehouse (DWH)](Consolidated_Data_Warehouse/)
A centralized "Source of Truth" for the Kenyan banking industry using CBK Bank Supervision data.
*   **Tech Stack**: Python (pdfplumber), PostgreSQL, dbt, Apache Airflow.
*   **Features**: Star-schema design, 10+ years of bank-level time-series data, automated KPI extraction (ROE, NIM, NPL).
*   **Dashboard**: `http://localhost:8504`

### 2. [AML Transaction Monitoring Rules Engine](AML_Transaction_Monitoring/)
A rules-based engine designed to detect suspicious financial activities based on FATF typologies and CBK guidelines.
*   **Tech Stack**: Python, Kafka (Messaging), Redis (Cache), PostgreSQL.
*   **Features**: Detection of Structuring (Smurfing), PEP matching, and unusual cash spikes.
*   **Dashboard**: Suspicious Activity Report (SAR) alerts and risk heatmaps.

### 3. [Peer Analysis & Normalization](Peer_Analysis/)
Comparative analytics for mid-tier banks (Stanbic, StanChart, DTB, I&M).
*   **Features**: Z-score normalization of financial KPIs, Scale vs. Profitability positioning matrices.

### 4. [Digital Banking Adoption Tracker](Digital_Banking_Adoption_Tracker/)
Monitoring the shift from brick-and-mortar to mobile/internet banking across the sector.
*   **Features**: Branch/ATM footprint reduction trends vs. digital transaction growth.

---

## Data Sources
The analytics in this sector portfolio are derived from:
- **Central Bank of Kenya (CBK)**: Bank Supervision Annual Reports (2015-2025), Prudential Guidelines, and AML/CFT reporting templates.
- **Financial Action Task Force (FATF)**: International AML typologies and smurfing detection patterns.
- **Nairobi Securities Exchange (NSE)**: Multi-year financial filings for all listed commercial banks in Kenya.

## 🛠 Tech Stack
*   **Orchestration**: Apache Airflow
*   **Data Warehouse**: PostgreSQL
*   **Transformation**: dbt (Data Build Tool)
*   **Visualisation**: Streamlit & Plotly
*   **Ingestion**: Python (Scrapy, Selenium, pdfplumber)
*   **Containerization**: Docker & Docker Compose

---

## 📊 Access & Monitoring
The entire sector is accessible via a unified **Master Dashboard**:
*   **Local URL**: `http://localhost:8501`
*   **Live Sector View**: `http://localhost:8504`

---
*Created by Victor Kipruto - Data Engineering Portfolio*
