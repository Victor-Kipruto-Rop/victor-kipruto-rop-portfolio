# 19. Absa Kenya Financial KPIs Warehouse

## Difficulty: Beginner | Impact: Medium

### Overview
Parse Absa Bank Kenya's annual reports and NSE filings post-rebranding (2020-present). Track transition from Barclays to Absa: brand investment impact on deposits, retail loan growth, SME banking penetration, and digital channel adoption vs incumbents.

### Tools Required
- Python (pdfplumber)
- dbt
- PostgreSQL
- Apache Airflow
- Metabase

### Kenyan Data Sources
- Absa Kenya Investor Relations
- NSE CDSC
- CBK Bank Supervision Annual Report

### Project Structure
```
absa-kpi-warehouse/
ingestion/
  absa_ir_scraper.py # Absa Group investor relations
  nse_parser.py # NSE filings for Absa Bank Kenya
  pdf_extractor.py # camelot-py: quarterly financials
dbt/models/
  staging/stg_absa_quarterly.sql
  marts/mart_profitability.sql
  marts/mart_asset_quality.sql
  marts/mart_efficiency_ratio.sql
  marts/mart_capital_adequacy.sql
seeds/
  kpi_definitions.csv
dags/
  quarterly_load_dag.py
tests/
notebooks/
docs/
├── dbt/
├── schemas/
├── airflow_dags/
└── dashboards/
```

### Key Deliverables
- Absa financial KPI warehouse
- Rebranding impact analysis
- Deposit growth tracking
- Loan segment analysis
- Digital adoption metrics
- Competitive benchmarking
- Metabase dashboards

### Next Steps
1. Collect Absa reports (2020+)
2. Get NSE filings
3. Build PDF parser
4. Extract KPI metrics
5. Set up PostgreSQL schema
6. Create rebranding analysis
7. Schedule Airflow pipelines
8. Build dashboards
