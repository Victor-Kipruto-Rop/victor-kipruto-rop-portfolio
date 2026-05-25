# 18. Equitel & EazzyPay Transaction Analytics

## Difficulty: Intermediate | Impact: Medium

### Overview
Combine Equitel MVNO subscriber data from CA Kenya and Equity's published EazzyPay volumes. Model mobile banking adoption curves, cross-sell rates to insurance/investment products, and ARPU trends vs M-Pesa Fuliza.

### Tools Required
- Python
- dbt
- PostgreSQL
- Apache Airflow
- Metabase

### Kenyan Data Sources
- CA Kenya Telecom Reports
- Equity Annual Report
- CBK Mobile Banking data

### Project Structure
```
equitel-eazzypay-analytics/
ingestion/
  ca_kenya_scraper.py # CA Kenya Equitel subscriber data
  equity_annual_parser.py # EazzyPay volume disclosures
  cbk_mobile_banking.py # CBK mobile banking statistics
dbt/models/
  staging/stg_equitel.sql
  staging/stg_eazzypay.sql
  marts/mart_adoption_curve.sql
  marts/mart_cross_sell_rate.sql
  marts/mart_arpu_benchmark.sql # vs M-Pesa Fuliza
notebooks/
  adoption_s_curve.ipynb
  arpu_comparison.ipynb
dags/
tests/
docs/
```

### Key Deliverables
- Equitel subscriber tracking
- EazzyPay volume analytics
- Mobile banking adoption curves
- Cross-sell rate analysis
- ARPU trend analysis
- Product mix insights
- Metabase dashboards

### Next Steps
1. Get CA Kenya telecom data
2. Collect Equity's EazzyPay volumes
3. Access CBK mobile banking stats
4. Set up PostgreSQL schema
5. Build adoption models
6. Create dbt models
7. Schedule Airflow pipelines
8. Deploy dashboards
