# 🚢 Customs & Trade Data Pipeline

![Status](https://img.shields.io/badge/Status-Implementation-blue)
![Difficulty](https://img.shields.io/badge/Difficulty-Advanced-red)

## 📋 Overview
An advanced trade intelligence pipeline that ingests KRA customs declaration data (HS codes, port of entry) and cross-references it with UN Comtrade volumes. It tracks commodity-level trade balances, duty collection, and contraband risk scoring.

## 🚀 Key Features
- **HS Code Tracking**: Granular monitoring of import/export commodity volumes.
- **Duty Analytics**: Identifying revenue leakages and under-valuation anomalies.
- **Risk Scoring**: Automated contraband risk scoring based on origin country and commodity type.

## Data Sources
- **UN Comtrade**: International trade database (HS-code level benchmarks).
- **ITC TradeMap Beta**: Kenyan trade corridors and mirror-statistics for discrepancy detection.
- **KRA Customs & Border Control**: National import/export declaration summaries and Rules of Origin disclosures.

## 🛠 Tech Stack
- **Data Ingestion**: Python (API-driven)
- **Database**: PostgreSQL
- **Modeling**: dbt
- **Monitoring**: Grafana

---
*Developed by Victor Kipruto - KRA Data Engineering Portfolio*
