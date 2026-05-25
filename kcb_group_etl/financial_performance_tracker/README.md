# 15. KCB Group Financial Performance Tracker

## Difficulty: Beginner | Impact: Medium

### Overview
Extract and ingest KCB Group quarterly earnings releases, NSE filings, and investor presentations. Build a financial KPI warehouse tracking NIM, ROE, NPL ratio, loans by segment, deposit mix, and subsidiary performance (Kenya, Uganda, Tanzania, Rwanda, Ethiopia).

### Tools Required
- Python (pdfplumber, camelot)
- dbt
- PostgreSQL
- Apache Airflow
- Metabase

### Kenyan Data Sources
- KCB Investor Relations
- NSE CDSC filings
- CBK Bank Supervision Report

### Project Structure
```
kcb-financial-tracker/
ingestion/
  kcb_ir_scraper.py # KCB investor relations page
  nse_filings.py # NSE quarterly/annual reports
  pdf_extractor.py # camelot-py: financial table extraction
  subsidiary_parser.py # Per-country subsidiary financials
dbt/models/
  staging/stg_kcb_group.sql
  staging/stg_kcb_subsidiaries.sql
  marts/mart_nim_trend.sql # Net Interest Margin
  marts/mart_npl_ratio.sql # Non-Performing Loans
  marts/mart_roe_roa.sql # Return on Equity/Assets
  marts/mart_subsidiary_perf.sql
seeds/
  subsidiary_currencies.csv # UGX, TZS, RWF exchange rates
dags/
tests/
notebooks/
docs/
```

### Key Deliverables
- PDF parsing for financial documents
- KPI database (NIM, ROE, NPL)
- Multi-subsidiary tracking
- Quarterly performance tracking
- PostgreSQL warehouse
- dbt transformation models
- Metabase dashboards

### Next Steps
1. Collect KCB quarterly releases
2. Download NSE filings
3. Build PDF parser
4. Extract KPI metrics
5. Set up PostgreSQL schema
6. Create dbt models
7. Schedule Airflow pipelines
8. Build Metabase dashboards
