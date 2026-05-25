# 16. KCB M-Pesa Loan Book Analytics

## Difficulty: Advanced | Impact: High

### Overview
Combine CBK mobile credit statistics with KCB M-Pesa product disclosures to model the KCB M-Pesa loan book growth, default rates, and customer tenure. Build a credit cohort analysis pipeline tracking vintage performance over time.

### Tools Required
- Python
- dbt
- PostgreSQL
- Apache Airflow
- Jupyter
- Superset

### Kenyan Data Sources
- CBK Mobile Credit Report
- KCB Annual Report
- CRB Africa sector data

### Project Structure
```
kcb-mpesa-loan-analytics/
ingestion/
  cbk_mobile_credit.py # CBK mobile credit statistics
  kcb_disclosures.py # KCB Annual Report KCB M-Pesa section
analysis/
  cohort_builder.py # Build loan origination cohorts
  vintage_analysis.py # 3/6/12-month default curves
  customer_lifetime.py # LTV of KCB M-Pesa borrower
dbt/models/
  marts/mart_loan_cohorts.sql
  marts/mart_vintage_performance.sql
  marts/mart_collection_efficiency.sql
notebooks/
  cohort_visualisation.ipynb
dags/
tests/
docs/
```

### Key Deliverables
- M-Pesa loan book database
- Customer cohort analysis
- Default rate tracking
- Vintage performance modeling
- Customer tenure analysis
- Growth trajectory forecasts
- Superset analytics dashboards

### Next Steps
1. Access CBK mobile credit data
2. Get KCB M-Pesa disclosures
3. Set up PostgreSQL schema
4. Build cohort tables
5. Create dbt models
6. Develop Jupyter notebooks
7. Schedule Airflow pipelines
8. Deploy dashboards
