# Kepler.gl Dashboard — Setup & Usage

## Quick Start

### Option 1: Use Kepler.gl Cloud (Recommended)

1. Visit https://kepler.gl
2. Click "Get Started" → "Sample Map" or drag/drop a file
3. Upload these GeoJSON files one-by-one or as a folder:
   - `data/kepler/agents.geojson` (120,000 agent locations)
   - `data/kepler/wards.geojson` (879 ward boundaries)
   - `data/kepler/grid.geojson` (agent density grid, 0.01° cells)

4. Layer configuration:
   - **Agents**: Point layer, color by transaction count, size by transactions
   - **Wards**: Polygon layer, fill color by agent_count, transparency 0.3
   - **Grid**: Hexagon/heatmap layer, color scale by total_transactions

### Option 2: Local Viewer

Open `maps/kepler_viewer.html` in a web browser (requires internet for Kepler.gl library).

### Option 3: Embed Config

Use `maps/kepler_dashboard_config.json` to load a pre-configured Kepler.gl instance.

---

## Data Dictionary

### agents.geojson (120,000 features)
- `agent_id`: Unique agent identifier (CBKAGENT*)
- `agent_name`: Agent business name
- `county`: County location
- `transactions`: Count of transactions for this agent
- `float_balance`: Agent's float balance (KES)
- `geometry`: Point (longitude, latitude in EPSG:4326)

### wards.geojson (879 features)
- `ward_code`: Ward identifier
- `ward_name`: Ward name
- `county`: County
- `agent_count`: Total agents in ward (aggregated)
- `total_transactions`: Sum of transactions in ward
- `geometry`: MultiPolygon ward boundary

### grid.geojson (10,000+ features)
- `grid_x`: Grid cell longitude
- `grid_y`: Grid cell latitude
- `agent_count`: Agents in grid cell
- `total_transactions`: Sum of transactions in cell
- `geometry`: Polygon grid cell (0.01° × 0.01°)

---

## Analysis Ideas

1. **Hotspot Detection**: Filter high agent_count grids (red zones) vs. underserved areas (blue zones)
2. **Ward Comparison**: Sort wards by agent_count or total_transactions; identify gaps
3. **Placement Recommendations**: Cluster low-density areas for new agent placement
4. **Commission Analysis**: Transaction count × avg commission (if added to model)

---

## Updating the Dashboard

To refresh data after new ingestion:

```bash
python3 ingestion/cbk_loader.py
python3 scripts/create_ward_aggregates.py
python3 spatial/ward_analysis.py
python3 scripts/export_for_kepler.py
python3 scripts/export_wards_geojson.py
```

Then re-upload GeoJSON files to Kepler.gl.

---

## Troubleshooting

- **File too large**: Limit grid export in `scripts/export_wards_geojson.py` (e.g., `LIMIT 5000`)
- **Slow rendering**: Reduce agent count by filtering or using grid layer only
- **Missing geometry**: Ensure PostGIS ingestion created valid geom column (check via `SELECT COUNT(*) FROM agents WHERE geom IS NOT NULL;`)

---

## Next Steps

- Export analysis results as charts (Kepler → Export CSV)
- Create a web dashboard using Mapbox + Chart.js
- Build Airflow DAG to refresh data daily
