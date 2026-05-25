# 8. Safaricom Network Quality Data Pipeline

## Difficulty: Intermediate | Impact: Medium

### Overview
Combine CA Kenya QoS reports, Ookla Speedtest open data, and crowdsourced OpenSignal metrics to build a ward-level Safaricom network quality index. Track 2G/3G/4G/5G coverage trends and correlate with M-Pesa transaction failure rates.

### Tools Required
- Python
- PostGIS
- dbt
- BigQuery
- Apache Airflow
- Leaflet.js

### Kenyan Data Sources
- CA Kenya QoS Reports (ca.go.ke)
- Ookla Open Data
- OpenSignal API

### Project Structure
```
safaricom-network-quality/
ingestion/
  ca_kenya_scraper.py # CA Kenya QoS PDF reports
  ookla_client.py # Ookla Speedtest open dataset
  opensignal_scraper.py # OpenSignal mobile experience data
dbt/models/
  staging/stg_qos_reports.sql
  staging/stg_speedtest.sql
  marts/mart_network_index.sql # Composite quality score
  marts/mart_coverage_by_ward.sql
spatial/
  coverage_analysis.py # PostGIS coverage polygon joins
maps/
  network_map.html # Leaflet.js choropleth map
seeds/
  kenya_wards.csv
dags/
tests/
notebooks/
docs/
```

### Key Deliverables
- CA Kenya QoS data ingestion
- Ookla Speedtest metrics
- OpenSignal crowdsourced data
- Ward-level network quality index
- Coverage trend analysis
- M-Pesa failure rate correlation
- Interactive maps (Leaflet.js)

### Next Steps
1. Access CA Kenya QoS reports
2. Set up Ookla API connection
3. Configure OpenSignal metrics
4. Build PostGIS database
5. Create ward-level polygons
6. Develop aggregation pipelines
7. Build correlation analysis
8. Deploy interactive maps
