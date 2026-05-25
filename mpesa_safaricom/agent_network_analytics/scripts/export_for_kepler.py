"""
export_for_kepler.py

Stream the ``agents`` table from PostGIS to
``data/kepler/agents.geojson`` for Kepler.gl / Leaflet.js / Mapbox.

Useful facts
------------
* ``ST_AsGeoJSON``  is executed server-side — rows are never fully
  materialised in Python before hitting the file.
* The GeoJSON ``Feature.properties`` record mirrors the schema expected
  by ``maps/kepler_dashboard_config.json`` so Kepler layers resolve without
  extra field mappings.
"""
import os
import json
from pathlib import Path
import logging

from sqlalchemy import create_engine, text   # pylint: disable=wrong-import-position

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_URL = os.getenv('MPESA_DATABASE_URL', 'postgresql://mpesa:mpesa_pass@localhost:5433/mpesa')
OUT_DIR: Path = Path(__file__).resolve().parents[1] / 'data' / 'kepler'
OUT_FILE: Path = OUT_DIR / 'agents.geojson'


def _row_to_feature(row: Any) -> dict | None:
    """Convert a SQLAlchemy Row to a GeoJSON Feature dict, or None on error."""
    try:
        keys = list(row.keys())
        geo  = row['geojson']
        if not geo:
            return None
        geometry = json.loads(geo)
        props    = {
            'agent_id':            int(row['agent_id'])   if row['agent_id'] is not None  else None,
            'agent_name':          row.get('agent_name'),
            'county':              row.get('county'),
            'ward':                row.get('ward'),
            'transactions':        int(row['transactions']   or 0),
            'total_transaction_amount': float(row.get('total_transaction_amount') or 0.0),
            'float_balance':       float(row.get('float_balance') or 0.0),
        }
        return {'type': 'Feature', 'geometry': geometry, 'properties': props}
    except Exception as exc:
        logger.warning("Skipping malformed row: %s", exc)
        return None


def export_agents(batch_size: int = 50_000,
                  out_dir: str | Path | None = None,
                  out_file: str | Path | None = None) -> dict[str, int]:
    """
    Stream the entire ``agents`` table to GeoJSON in batches to avoid
    loading 100k+ rows into memory at once.

    Returns
    -------
    dict  {'rows_written': int, 'skipped': int}
    """
    dest_dir  = Path(out_dir  or OUT_DIR)
    dest_file = Path(out_file or OUT_FILE)
    dest_dir.mkdir(parents=True, exist_ok=True)

    engine = create_engine(DB_URL)
    sql = text(
        "SELECT agent_id, agent_name, county, ward, "
        "       transactions, total_transaction_amount, float_balance, "
        "       ST_AsGeoJSON(geom) AS geojson "
        "FROM agents WHERE geom IS NOT NULL;"
    )

    rows_written = 0
    skipped      = 0
    with engine.connect() as conn, open(dest_file, 'w', encoding='utf-8') as fh:
        fh.write('{"type": "FeatureCollection", "features": [\n')
        first = True
        for batch in pd.read_sql(sql, conn, chunksize=batch_size).itertuples(index=False, name=None):
            row = dict(zip(
                ['agent_id', 'agent_name', 'county', 'ward',
                 'transactions', 'total_transaction_amount', 'float_balance', 'geojson'],
                batch,
            ))
            feature = _row_to_feature(row)
            if feature is None:
                skipped += 1
                continue
            prefix = '' if first else ',\n'
            fh.write(f'{prefix}{json.dumps(feature)}')
            first = False
            rows_written += 1
        fh.write('\n]}\n')

    size_mb = dest_file.stat().st_size / 1_048_576
    logger.info("✓ wrote %d features (%d skipped) → %s (%.1f MB)",
                rows_written, skipped, dest_file, size_mb)
    return {'rows_written': rows_written, 'skipped': skipped}


if __name__ == '__main__':
    export_agents()
