"""
create_ward_aggregates.py

Build / refresh the ``ward_agent_aggregates`` table, the single source of
truth for ward-level metrics consumed by dbt, spatial analytics, and all
export scripts.

Metrics produced per ward
-------------------------
agent_count           unique agents whose geometry falls inside the ward
total_transactions    SUM(agents.transactions)
total_float           SUM(agents.float_balance)
avg_float_balance     AVG(agents.float_balance)
float_util_ratio      total_float / total_transactions  (0 when no transactions)
float_below_threshold # agents whose float_balance < FLOAT_ALERT_THRESHOLD KES
geom                  ward polygon if available; NULL otherwise
"""
import os
import logging
from pathlib import Path

from sqlalchemy import create_engine, text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_URL          = os.getenv('MPESA_DATABASE_URL', 'postgresql://mpesa:mpesa_pass@localhost:5433/mpesa')
FLOAT_THRESHOLD = 50_000.0   # KES


def create(output_dir: str | Path | None = None) -> None:
    engine = create_engine(DB_URL)
    with engine.begin() as conn:
        conn.execute(text('CREATE EXTENSION IF NOT EXISTS postgis;'))

        # ── Rebuild aggregates ──────────────────────────────────────────────
        conn.execute(text('DROP TABLE IF EXISTS ward_agent_aggregates;'))
        conn.execute(text("""
            CREATE TABLE ward_agent_aggregates AS
              SELECT w.ward_code, w.ward_name, w.county, w.geom,
                     COUNT(a.agent_id)                                                        AS agent_count,
                     COALESCE(SUM(a.transactions), 0)                                         AS total_transactions,
                     COALESCE(SUM(a.float_balance), 0.0)                                       AS total_float,
                     ROUND(COALESCE(AVG(a.float_balance), 0.0), 2)                            AS avg_float_balance,
                     CASE WHEN COALESCE(SUM(a.transactions), 0) > 0
                          THEN ROUND(COALESCE(SUM(a.float_balance), 0.0)
                                      / SUM(a.transactions), 6)
                          ELSE 0.0
                     END                                                                      AS float_util_ratio,
                     SUM(CASE WHEN a.float_balance < :thresh THEN 1 ELSE 0 END)              AS float_below_threshold
              FROM wards w
              LEFT JOIN agents a
                     ON (w.geom IS NOT NULL
                         AND a.geom IS NOT NULL
                         AND ST_Contains(w.geom, a.geom))
                     OR (w.geom IS NULL
                         AND lower(coalesce(a.ward, '')) = lower(coalesce(w.ward_name, '')))
              GROUP BY w.ward_code, w.ward_name, w.county, w.geom;
        """), {'thresh': FLOAT_THRESHOLD})

        conn.execute(text(
            "CREATE INDEX IF NOT EXISTS idx_ward_agent_aggs_geom "
            "ON ward_agent_aggregates USING GIST (geom);"
        ))

    # ── Quick summary to stdout ─────────────────────────────────────────────
    df = pd.read_sql(
        text('SELECT ward_code, ward_name, agent_count, total_transactions, '
             'total_float, avg_float_balance, float_below_threshold '
             'FROM ward_agent_aggregates '
             'ORDER BY agent_count DESC LIMIT 20;'),
        create_engine(DB_URL),
    )
    print(df.to_string(index=False))
    logger.info('✓ ward_agent_aggregates refreshed (%d wards).', len(df))


if __name__ == '__main__':
    import pandas as pd
    create()
