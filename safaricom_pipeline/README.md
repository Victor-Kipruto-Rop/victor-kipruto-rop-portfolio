# 📱 Safaricom PLC Integrated Data Pipeline

This directory contains the integrated data engineering pipelines for Safaricom PLC, covering financial results, mobile credit risk (Fuliza), loyalty systems (Bonga), and network quality monitoring.

## 🚀 Overview

The platform provides a high-fidelity 360-degree view of Safaricom PLC's ecosystem. It utilizes a custom **Analytics Engine** that integrates audited financial disclosures, mobile credit risk modeling (Fuliza), and regional network quality benchmarks (CA Kenya).

## 🛠️ Integrated Projects

| Project Name | Tech Stack | Description |
| :--- | :--- | :--- |
| [Financial Results Warehouse](./Financial_Results_Warehouse) | `Python`, `BeautifulSoup`, `SQL` | Automated extraction of financial metrics from audited IR reports (2021-2025). |
| [Fuliza Credit Risk Analytics](./Fuliza_Credit_Risk_Analytics) | `Python`, `Pandas`, `Numpy` | Portfolio quality modeling for Fuliza disbursements (~KES 700B/year) and NPL evolution. |
| [Bonga Loyalty Analytics](./Bonga_Loyalty_Analytics) | `Python`, `NLP`, `SQL` | Segmentation and redemption efficiency modeling for Safaricom's Bonga Points ecosystem. |
| [Network Quality Pipeline](./Network_Quality_Pipeline) | `Python`, `Spatial`, `API` | Real-time regional performance tracking (Latency/Speed) across Kenya's telecom corridors. |

## 📊 Integrated Analytics Dashboard

The platform includes a comprehensive multi-tab Streamlit dashboard providing real-time visibility into Safaricom's ecosystem.

### Key Features:
- **💰 Financial Results**: Year-on-Year growth tracking for Revenue (KES 335B+), EBITDA, and Net Profit.
- **🛡️ Fuliza Credit Risk**: Monthly disbursement trends and Portfolio Risk (NPL %) evolution by cohort.
- **🎁 Bonga Loyalty**: Segmentation of active loyalty users and redemption efficiency metrics.
- **📡 Network Quality**: Regional performance matrix comparing latency vs. download speed across Kenya.

### Accessing the Dashboards:
1. **Interactive Dashboard (Streamlit)**: 
   - **Live Demo**: [🚀 View Safaricom Integrated Dashboard](https://kipruto45-victor-kipruto-rop-portfolio-g8pspygfpttsbfggjaadwy.streamlit.app/)
   - **Local URL**: [http://localhost:8513](http://localhost:8513)
   - **Command**: `streamlit run dashboard_app.py` from the project root.
2. **Master Hub**: Accessible via the [Master Dashboard](../master_dashboard.py).

## Data Sources

This project utilizes the following real-world datasets:
- **Safaricom Investor Relations**: Audited FY 2024/25 Annual Reports and Financial Statements.
- **GSMA Mobile Money**: Industry benchmarks for mobile credit and agent transaction volumes.
- **Network Performance Logs**: Simulated regional availability and speed metrics aligned with CA Kenya standards.
- **Bonga Redemption Logs**: Anonymized redemption patterns and sentiment data from customer feedback channels.

---
*Maintained by the Data Engineering Team*
