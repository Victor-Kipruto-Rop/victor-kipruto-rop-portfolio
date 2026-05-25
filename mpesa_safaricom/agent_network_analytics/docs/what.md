# docs/what.md

## What this project does

The **Agent Network Analytics** pipeline ingests M-Pesa agent-banking data,
transforms it through PostGIS + dbt, and produces geospatial analytics and
executable visualisations.

### Data flow

```
CBK PDFs / CSV / Excel  ── ingestion/pdf_extractor.py + cbk_loader.py  ──►  PostGIS / agents
                                                                                      │
                                                                                dbt / staging models
                                                                                      │
                                                                            dbt / mart: density + float coverage
                                                                                      │
                                                          scripts/create_ward_aggregates.py, spatial/ward_analysis.py
                                                                                      │
                                     ┌─────────────────────────────────────────────────┘
                                     │
                               data/kepler/*.geojson (Kepler / Leaflet / Mapbox dashboards)
                                     │
                                   data/reports/*.csv (static / Power BI feeds)
                                     │
                     Airflow DAGs / dags/refresh_daily_dag.py  — nightly run

### Key metrics produced

| Metric              | Table / file              | Primary consumer           |
|---------------------|--------------------------|----------------------------|
| Agent count         | agents                   | DAG QC, dashboards         |
| Ward density        | marts.mart_agent_density  | Kepler layers, CSV reports |
| Float coverage      | marts.mart_float_coverage | Dashboard, CSV reports     |
| Grid density        | agent_density_grid       | Kepler / Leaflet heatmap   |
| Placement suggestions| agent_placement_suggestions | Optimal_placement.py     |

### What's left

See `TODO_REMAINING.md` for a concise gap list.  High-priority items:

1. **`seeds/`** — ward boundary GADM shapefile not yet loaded; ward-level
   aggregations fall back to name-join.
2. **`maps/`** — `kepler_viewer.html` needs a valid Mapbox token and a
   `dataId` match against `kepler_dashboard_config.json`.
3. **Airflow CI** — DAGs are production-shaped but have not been smoke-
   tested in a live Airflow container.
4. **Safaricom API key** — `geospatial_scraper.fetch_agents_by_county`
   raises ``RuntimeError`` until ``SAFARICOM_API_KEY`` is set in the env.

### Environment variables

| Variable             | Purpose                                   | Default (dev)                        |
|----------------------|-------------------------------------------|--------------------------------------|
| `MPESA_DATABASE_URL` | PostGIS connection string                 | `postgresql://mpesa:mpesa_pass@…`   |
| `SAFARICOM_API_KEY`  | Safaricom agent locator bearer token      | *(unset — raises RuntimeError)*      |
| `MAPBOX_TOKEN`       | Mapbox GL token for maps                  | dummy Key for demo                   |
| `POSTGRES_*`         | Credentials consumed by Docker Compose    | see `.env.sample`                    |
| `GEOCODER_USER_AGENT`| User-Agent header for Nominatim geocoding | `mpesa-agent-analytics/1.0`          |
