# 🛡️ AML / Transaction Monitoring Rules Engine

![Status](https://img.shields.io/badge/Status-Robust-green)
![Difficulty](https://img.shields.io/badge/Difficulty-Advanced-red)

## 📋 Overview
A sophisticated, rules-based Anti-Money Laundering (AML) monitoring system tailored for the Kenyan banking context. This engine detects suspicious transaction patterns using FATF typologies and CBK AML/CFT guidelines, providing compliance officers with an automated alerting system.

## 🚀 Key Features
- **Structuring Detection**: Identifies accounts attempting to bypass the 1M KES reporting threshold through multiple smaller deposits (smurfing).
- **PEP Screening**: Automated flagging of high-value transactions involving Politically Exposed Persons (PEPs).
- **Synthetic Data Ingestion**: Custom Python generator producing high-fidelity transaction streams for stress-testing.
- **SAR Dashboard**: A Streamlit-based interface for managing Suspicious Activity Reports (SARs).

## 🛠 Tech Stack
- **Engine**: Python 3.x
- **Data Handling**: Pandas & NumPy
- **Visualisation**: Streamlit & Plotly
- **Orchestration**: Docker Compose (Integrated Sector Stack)

## 📁 Project Structure
```bash
AML_Transaction_Monitoring/
├── data/               # Synthetic transaction storage
├── ingestion/          # Python data generators
├── src/                # Core Rules Engine logic
├── dashboard_app.py    # Streamlit interface
└── README.md           # This file
```

## 📊 Quick Start
To view the AML dashboard within the sector stack:
1. Ensure the sector environment is running: `docker compose up -d`
2. Access the AML monitor: `http://localhost:8505`

---
*Developed as part of the Kenya Banking Sector Analytics Portfolio*
