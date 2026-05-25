"""
export_wards_geojson.py

Stream ``ward_agent_aggregates`` (PostGIS) → ``data/kepler/wards.geojson``.
Uses positional row access by column-name look-up so that schema changes
don't silently shift indexes.
"""
import os
import json
from pathlib import Path
import logging

from sqlalchemy import create_engine, text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_URL   = os.getenv('MPESA_DATABASE_URL', 'postgresql://mpesa:mpesa_pass@localhost:5433/mpesa')
OUT_DIR: Path = Path(__file__).resolve().parents[1] / 'data' / 'kepler'
OUT_FILE: Path = OUT_DIR / 'wards.geojson'

_COL: dict[str, str] = {
    'ward_code':        'ward_code',
    'ward_name':        'ward_name',
    'county':           'county',
    'agent_count':      'agent_count',
    'total_transactions':'total_transactions',
    'total_float':      'total_float',
    'avg_float_balance':'avg_float_balance',
    'float_below_threshold': 'float_below_threshold',
    'geojson':          'geojson',
}


def _safe(val: Any, cast: type = str, default: Any = None) -> Any:
    """Return *val* cast to *cast*, or *default* on failure."""
    try:
        return cast(val)
    except (TypeError, ValueError):
        return default


def export_wards(out_file: str | Path | None = None) -> dict[str, int]:
    """
    Write ``ward_agent_aggregates`` (with geometry) to a GeoJSON file.

    Returns
    -------
    dict  {'features_written': int}
    """
    dest  = Path(out_file or OUT_FILE)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    engine = create_engine(DB_URL)
    sql = text("""
        SELECT ward_code, ward_name, county, agent_count, total_transactions,
               total_float, avg_float_balance, float_below_threshold,
               ST_AsGeoJSON(geom) AS geojson
        FROM ward_agent_aggregates
        WHERE geom IS NOT NULL
        ORDER BY ward_name;
    """)

    COLS = list(_COL.values())
    features = []
    with engine.connect() as conn:
        for row in conn.execute(sql):
            geo = row['geojson'] if 'geojson' in row.keys() else row[-1]
            if not geo:
                continue
            props = {key: _safe(row[key]) for key in _COL if key != 'geojson'}
            features.append({'type': 'Feature', 'geometry': json.loads(geo), 'properties': props})

    fc = {'type': 'FeatureCollection', 'features': features}
    with open(dest, 'w', encoding='utf-8') as fh:
        json.dump(fc, fh, indent=2)

    size_kb = dest.stat().st_size / 1024
    logger.info("✓ wrote %d ward features → %s (%.1f KB)", len(features), dest, size_kb)
    return {'features_written': len(features)}


if __name__ == '__main__':
    export_wards()
