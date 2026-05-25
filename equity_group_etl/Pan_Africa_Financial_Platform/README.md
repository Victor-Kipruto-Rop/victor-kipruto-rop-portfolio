# 17. Equity Group Pan-Africa Financial Data Platform

## Difficulty: Intermediate | Impact: High

### Overview
Ingest Equity Group results across all 7 subsidiaries (Kenya, DRC, Uganda, Tanzania, Rwanda, South Sudan, Ethiopia). Normalise currencies to USD and KES, build a group-level consolidation model in dbt, and track inter-subsidiary funding flows.

### Tools Required
- Python
- dbt
- Snowflake
- Apache Airflow
- Superset
- forex API

### Kenyan Data Sources
- Equity Group NSE filings
- Subsidiary central bank reports
- ExchangeRate-API

### Project Structure
```
equity-group-platform/
ingestion/
  equity_ir_scraper.py # Equity Group investor relations
  nse_filings.py
  subsidiary_parsers/
    kenya_parser.py
    drc_parser.py # DRC Congo subsidiary
    uganda_parser.py
    tanzania_parser.py
    rwanda_parser.py
    ethiopia_parser.py
forex/
  fx_client.py # ExchangeRate-API for KES/USD/UGX etc.
  fx_normalizer.py # Convert all figures to KES + USD
dbt/models/
  staging/stg_equity_*.sql # One per subsidiary
  marts/mart_group_consolidation.sql
  marts/mart_subsidiary_comparison.sql
  marts/mart_interco_flows.sql
seeds/
  subsidiaries.csv
dags/
tests/
notebooks/
docs/
```

### Key Deliverables
- Multi-subsidiary financial database
- Currency normalization (USD/KES)
- Group-level consolidation model
- Inter-subsidiary funding tracking
- Snowflake data warehouse
- dbt consolidation models
- Superset dashboards

### Next Steps
1. Access Equity Group NSE filings
2. Gather subsidiary reports (7 countries)
3. Set up forex API integration
4. Build Snowflake warehouse
5. Create dbt consolidation models
6. Develop currency normalization
7. Schedule Airflow pipelines
8. Deploy dashboards
