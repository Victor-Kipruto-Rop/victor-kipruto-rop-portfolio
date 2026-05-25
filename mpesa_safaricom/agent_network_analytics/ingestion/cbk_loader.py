"""
cbk_loader.py

Loads CBK agent CSV/Excel files from data/cbk, validates, normalises columns,
and writes to PostGIS using SQLAlchemy + GeoAlchemy2.  Fully idempotent,
retried on transient DB errors, and validates coordinates.
"""
import os
import glob
import logging
import time
import random
from pathlib import Path
from typing import Any, Optional

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, SQLAlchemyError

try:
    from geoalchemy2 import Geometry
except Exception:   # pragma: no cover - optional dependency in test env
    Geometry = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_URL          = os.getenv('MPESA_DATABASE_URL', 'postgresql://mpesa:mpesa_pass@localhost:5433/mpesa')
DATA_DIR        = Path(__file__).resolve().parents[1] / 'data' / 'cbk'
MAX_RETRIES     = 3
BACKOFF_BASE    = 2.0   # exponential back-off base (s)
FLOAT_THRESHOLD = 50_000.0   # KES — used for validation alerts

# Column variants that are normalised to standard names
RENAME_MAP: dict[str, str] = {
    'id':                 'agent_id',
    'name':               'agent_name',
    'lat':                'latitude',
    'lon':                'longitude',
    'lng':                'longitude',
    'float':              'float_balance',
    'transactions_count': 'transactions',
    'transaction_amount': 'transaction_amount',
}

REQUIRED_COLUMNS = ['agent_id', 'agent_name', 'county', 'ward',
                    'location', 'latitude', 'longitude',
                    'transactions', 'float_balance']


# ── File discovery ────────────────────────────────────────────────────────────

def discover_files(directory=DATA_DIR) -> list[str]:
    """Return sorted list of CSV/XLSX files in *directory*."""
    files: list[str] = []
    for ext in ('csv', 'xlsx', 'xls'):
        files.extend(glob.glob(str(Path(directory) / f"*.{ext}")))
    return sorted(files)


def read_file(path: str) -> pd.DataFrame:
    """Read a single CSV or Excel file into a DataFrame."""
    path = str(path)
    if path.lower().endswith('.csv'):
        return pd.read_csv(path)
    return pd.read_excel(path)


# ── Normalisation ────────────────────────────────────────────────────────────

def normalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise column names, rename common variants, and coerce types."""
    # 1. lower-case + strip
    df.columns = [c.strip().lower() for c in df.columns]

    # 2. rename known variants
    for src, dst in RENAME_MAP.items():
        if src in df.columns and dst not in df.columns:
            df = df.rename(columns={src: dst})

    # 3. ensure every required column exists
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            df[col] = None

    # 4. coerce types
    df['latitude']  = pd.to_numeric(df['latitude'],  errors='coerce')
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
    if 'transactions' in df.columns:
        df['transactions'] = pd.to_numeric(df['transactions'], errors='coerce').fillna(0).astype(int)
    if 'total_transaction_amount' not in df.columns:
        df['total_transaction_amount'] = pd.to_numeric(
            df.get('transaction_amount', pd.Series([0.0] * len(df))), errors='coerce'
        ).fillna(0.0)
    for col in ('float_balance', 'total_transaction_amount'):
        df[col] = pd.to_numeric(df.get(col, pd.Series([0.0] * len(df))), errors='coerce').fillna(0.0)

    # 5. coordinate range validation
    lat_invalid  = (df['latitude'].abs() > 90)  | df['latitude'].isna()
    lon_invalid  = (df['longitude'].abs() > 180) | df['longitude'].isna()
    df['latitude']  = df['latitude'].where(~lat_invalid)
    df['longitude'] = df['longitude'].where(~lon_invalid)

    # 6. WKT geometry
    df['geom_wkt'] = df.apply(
        lambda r: f"POINT({r['longitude']} {r['latitude']})"
        if pd.notnull(r['longitude']) and pd.notnull(r['latitude'])
        else None,
        axis=1,
    )
    return df


# ── Database write ───────────────────────────────────────────────────────────

def _execute_with_retry(conn: Any, sql: str, params: Optional[dict] = None) -> None:
    """Execute *sql* against *conn* with up to MAX_RETRIES exponential back-off."""
    last_exc: Optional[Exception] = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            conn.execute(text(sql), params or {})
            return
        except OperationalError as exc:
            last_exc = exc
            delay = BACKOFF_BASE ** attempt + random.uniform(0, 1)
            logger.warning("DB attempt %d/%d failed: %s — retrying in %.1fs",
                           attempt, MAX_RETRIES, exc, delay)
            time.sleep(delay)
    raise last_exc  # type: ignore[misc]


def write_to_postgis(df: pd.DataFrame, table_name: str = 'agents') -> None:
    """Idempotent upsert of *df* rows into *table_name* in PostGIS."""
    engine = create_engine(DB_URL)
    with engine.begin() as conn:
        # DDL — done once per session, not inside the per-row loop
        conn.execute(text(
            f"CREATE TABLE IF NOT EXISTS {table_name} "
            "(agent_id TEXT PRIMARY KEY, agent_name TEXT, county TEXT, ward TEXT, "
            "transactions BIGINT, total_transaction_amount DOUBLE PRECISION, "
            "float_balance DOUBLE PRECISION);"
        ))
        conn.execute(text(
            f"ALTER TABLE {table_name} "
            "ADD COLUMN IF NOT EXISTS geom geometry(Point,4326);"
        ))

        # DML — row-by-row upsert using parameterised query
        upsert_sql = f"""
            INSERT INTO {table_name}
                (agent_id, agent_name, county, ward,
                 transactions, total_transaction_amount, float_balance, geom)
            VALUES
                (:agent_id, :agent_name, :county, :ward,
                 :transactions, :total_transaction_amount, :float_balance,
                 ST_GeomFromText(:wkt, 4326))
            ON CONFLICT (agent_id) DO UPDATE SET
                agent_name            = EXCLUDED.agent_name,
                county                = EXCLUDED.county,
                ward                  = EXCLUDED.ward,
                transactions          = EXCLUDED.transactions,
                total_transaction_amount = EXCLUDED.total_transaction_amount,
                float_balance         = EXCLUDED.float_balance,
                geom                  = ST_GeomFromText(:wkt, 4326);
        """

        # Validate geom_wkt before insert; skip rows with bad WKT
        good = df[df['geom_wkt'].notna() & (df['agent_id'].notna())]
        skipped = int(len(df) - len(good))
        if skipped:
            logger.warning("Skipping %d rows with missing agent_id or null geometry.", skipped)

        rows = [
            {
                'agent_id':              str(r['agent_id']),
                'agent_name':            r.get('agent_name'),
                'county':                r.get('county'),
                'ward':                  r.get('ward'),
                'transactions':          int(r.get('transactions') or 0),
                'total_transaction_amount': float(r.get('total_transaction_amount') or 0.0),
                'float_balance':         float(r.get('float_balance') or 0.0),
                'wkt':                   r['geom_wkt'],
            }
            for _, r in good.iterrows()
        ]

        if rows:
            _execute_with_retry(conn, upsert_sql, rows)  # type: ignore[arg-type]

        # Spatial index — idempotent
        conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_geom "
                          f"ON {table_name} USING GIST (geom);"))

    logger.info('Upserted %d rows into %s.', len(rows), table_name)


# ── Transaction-level aggregation ────────────────────────────────────────────

def _detect_transaction_level(files: list[str]) -> bool:
    """Peek at column headers to decide whether CSV contains raw transactions."""
    for f in files:
        try:
            cols = pd.read_csv(f, nrows=0).columns.str.lower()
            if any(c in cols for c in ('transaction_amount', 'transaction_id', 'transaction_type')):
                return True
        except Exception:
            continue
    return False


def _aggregate_by_agent(parts: list[pd.DataFrame]) -> pd.DataFrame:
    """Group transaction-level rows to one row per agent_id."""
    raw = pd.concat(parts, ignore_index=True)
    agg = raw.groupby('agent_id', as_index=False).agg(
        agent_name=('agent_name', lambda x: x.dropna().iloc[0] if len(x.dropna()) > 0 else None),
        county=('county',       lambda x: x.dropna().iloc[0] if len(x.dropna()) > 0 else None),
        ward=('ward',           lambda x: x.dropna().iloc[0] if len(x.dropna()) > 0 else None),
        latitude=('latitude',   'first'),
        longitude=('longitude', 'first'),
        transactions=('transaction_id', 'count'),
        total_transaction_amount=('transaction_amount', 'sum'),
    )
    # float_balance was not in raw transactions; keep 0.0
    agg['float_balance'] = 0.0
    agg['geom_wkt'] = agg.apply(
        lambda r: f"POINT({r['longitude']} {r['latitude']})"
        if pd.notnull(r['longitude']) and pd.notnull(r['latitude']) else None,
        axis=1,
    )
    return agg


# ── Main pipeline ─────────────────────────────────────────────────────────────

def run(directory: Optional[str | Path] = None) -> None:
    """Discover → read → normalise → upsert all CBK files."""
    src_dir = Path(directory) if directory else DATA_DIR
    src_dir.mkdir(parents=True, exist_ok=True)

    files = discover_files(src_dir)
    if not files:
        logger.warning('No CBK data files found in %s', src_dir)
        return

    if _detect_transaction_level(files):
        logger.info('Transaction-level data detected; aggregating per agent ...')
        parts = []
        for f in files:
            logger.info('Reading %s ...', f)
            parts.append(normalise_columns(read_file(f)))
        agg = _aggregate_by_agent(parts)
        write_to_postgis(agg)
        logger.info('Aggregated %d agents from transaction data.', len(agg))
    else:
        total = 0
        for f in files:
            logger.info('Ingesting %s ...', f)
            df  = normalise_columns(read_file(f))
            write_to_postgis(df)
            total += len(df)
        logger.info('Processed %d total rows from %d files.', total, len(files))


if __name__ == '__main__':
    run()
