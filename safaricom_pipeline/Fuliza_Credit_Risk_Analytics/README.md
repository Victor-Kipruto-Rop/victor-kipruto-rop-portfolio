# 9. Fuliza (Overdraft) Credit Risk Analytics

## Difficulty: Advanced | Impact: High

### Overview
Model Safaricom Fuliza usage patterns using public CBK mobile credit data. Segment users by overdraft frequency and repayment speed, detect rollover risk, and build a scorecard that predicts non-repayment using transaction behavioural features.

### Tools Required
- Python (scikit-learn, pandas)
- dbt
- PostgreSQL
- MLflow
- Apache Airflow
- Superset

### Kenyan Data Sources
- CBK Mobile Credit Statistics
- Safaricom annual report Fuliza disclosures
- CRB Africa data

### Project Structure
```
fuliza-credit-risk/
ingestion/
  cbk_mobile_credit.py # CBK mobile lending statistics
  annual_report_parser.py # Safaricom Fuliza disclosures
features/
  behavioural_features.py # Transaction frequency, amounts
  repayment_features.py # Days to repay, rollover count
models/
  credit_scorecard.py # Logistic regression scorecard
  cohort_analysis.py # Vintage performance tracking
  pd_model.py # Probability of Default model
dbt/models/
  marts/mart_fuliza_cohorts.sql
  marts/mart_default_rates.sql
notebooks/
  eda_fuliza_usage.ipynb
  model_validation.ipynb
dags/
tests/
docs/
```

### Key Deliverables
- User behavior segmentation
- Fuliza usage patterns
- Repayment speed analysis
- Rollover risk detection
- Non-repayment prediction model (scikit-learn)
- Risk scorecards
- Superset analytics dashboards

### Next Steps
1. Access CBK mobile credit statistics
2. Gather Fuliza transaction data
3. Engineer behavioral features
4. Build user segmentation
5. Train risk prediction model
6. Create risk scorecards
7. Set up MLflow tracking
8. Deploy dashboards
