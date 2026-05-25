# 10. M-PESA App & Bonga Points Loyalty Analytics

## Difficulty: Intermediate | Impact: Medium

### Overview
Ingest public Bonga Points redemption categories, partner merchant data, and Safaricom app store reviews. Build a loyalty programme analytics product tracking redemption rates by category, partner performance, and customer sentiment via NLP on app reviews.

### Tools Required
- Python (spaCy, VADER)
- PostgreSQL
- dbt
- Airflow
- Grafana

### Kenyan Data Sources
- Google Play / App Store scrapes
- Safaricom partner portal
- Bonga catalogue

### Project Structure
```
bonga-loyalty-analytics/
ingestion/
  appstore_scraper.py # Google Play & App Store reviews
  bonga_catalogue.py # Scrape Bonga redemption categories
  partner_scraper.py # Safaricom partner directory
nlp/
  sentiment_analysis.py # VADER + spaCy on app reviews
  topic_modelling.py # LDA: what users complain about
  language_detection.py # Handles Swahili + English reviews
dbt/models/
  staging/stg_reviews.sql
  staging/stg_redemptions.sql
  marts/mart_sentiment_trends.sql
  marts/mart_partner_performance.sql
dags/
  weekly_review_scrape_dag.py
tests/
notebooks/
docs/
```

### Key Deliverables
- App store review scraping
- Sentiment analysis (VADER, spaCy)
- Redemption rate tracking
- Partner performance metrics
- Loyalty program analytics
- Grafana dashboards
- Customer sentiment insights

### Next Steps
1. Set up app store scraping
2. Collect Bonga redemption data
3. Build sentiment analysis pipeline
4. Create PostgreSQL schema
5. Develop dbt models
6. Set up Airflow DAGs
7. Build Grafana dashboards
