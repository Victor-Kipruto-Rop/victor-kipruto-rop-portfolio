# 7. Safaricom Financial Results Data Warehouse

## Difficulty: Beginner | Impact: Medium

### Overview
Parse and ingest all Safaricom annual reports and half-year investor presentations (2010-present) from their investor relations page. Extract KPIs (subscribers, ARPU, revenue by segment, EBITDA, M-Pesa revenue) into a time-series warehouse and build a trend dashboard.

### Tools Required
- Python (pdfplumber, camelot)
- PostgreSQL
- dbt
- Apache Airflow
- Metabase

### Kenyan Data Sources
- Safaricom Investor Relations (safaricom.co.ke/investor-relations)
- NSE filings

### Project Structure
```
safaricom-financial-dw/
ingestion/
  ir_scraper.py # Scrape safaricom.co.ke/investor-relations
  pdf_parser.py # pdfplumber: extract income statement tables
  nse_client.py # NSE filings downloader
  normalizer.py # Standardise KPI names across years
dbt/models/
  staging/stg_annual_results.sql
  staging/stg_half_year.sql
  marts/mart_revenue_by_segment.sql # M-Pesa, Voice, Data, Fixed
  marts/mart_subscriber_trends.sql
  marts/mart_ebitda_bridge.sql
seeds/
  kpi_definitions.csv # Canonical KPI name mapping
dags/
  results_ingestion_dag.py
tests/
notebooks/
docs/
```

### Key Deliverables
- PDF parsing & extraction logic
- KPI time-series database
- PostgreSQL data warehouse
- dbt transformations
- Metabase dashboards
- Trend analysis reports

### Next Steps
1. Collect Safaricom annual reports (2010-present)
2. Build PDF parser with pdfplumber/camelot
3. Extract KPIs manually & train extraction model
4. Set up PostgreSQL schema
5. Create dbt models
6. Schedule Airflow DAGs
7. Build Metabase dashboards
