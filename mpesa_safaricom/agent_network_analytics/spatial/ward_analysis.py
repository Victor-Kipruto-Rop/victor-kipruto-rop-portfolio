"""
ward_analysis.py

Spatial analytics on M-Pesa agent data using PostGIS.

Functions
---------
create_grid_summary(cell_size=0.02)
    Builds the ``agent_density_grid`` table — a regular latitude/longitude
    grid with agent counts and transaction totals per cell.  Returns the
    top-50 grid cells by agent count.

ward_agent_summary(limit=1000)
    Ward-level jointure: joins ``wards.geom`` → ``agents.geom`` via
    ``ST_Contains``; falls back to ``create_grid_summary`` when ward
    geometry is unavailable.  Returns a DataFrame of
    ``[ward_name, agent_count, total_transactions]``.

analysis_summary(limit=50)
    Convenience wrapper — caller can use this in a single DAG step
    instead of running multiple scripts.
"""
import os
import logging
import json

import pandas as pd
from sqlalchemy import create_engine, text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_URL  = os.getenv('MPESA_DATABASE_URL', 'postgresql://mpesa:mpesa_pass@localhost:5433/mpesa')
POSTGIS_EXTENSION_ENSURED = False   # idempotent flag


def _ensure_postgis(conn: Any) -> None:
    global POSTGIS_EXTENSION_ENSURED
    if not POSTGIS_EXTENSION_ENSURED:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        POSTGIS_EXTENSION_ENSURED = True


def create_grid_summary(cell_size: float = 0.02,
                        table_name: str = 'agent_density_grid') -> pd.DataFrame:
    """
    Build a regular grid-based agent density table.

    Parameters
    ----------
    cell_size : grid cell size in **degrees** (~2 km ≈ 0.02° at the
        Kenyan equator).
    table_name : PostGIS table name to create / replace.

    Returns
    -------
    pd.DataFrame   top-50 rows sorted by agent count descending.
    """
    engine = create_engine(DB_URL)
    with engine.begin() as conn:
        _ensure_postgis(conn)
        conn.execute(text(f"DROP TABLE IF EXISTS {table_name};"))
        conn.execute(text(f"""
            CREATE TABLE {table_name} AS
            WITH pts AS (
                SELECT *,
                    floor(ST_X(geom) / :cell_size) * :cell_size AS grid_x,
                    floor(ST_Y(geom) / :cell_size) * :cell_size AS grid_y
                FROM agents
                WHERE geom IS NOT NULL
            )
            SELECT ST_SetSRID(
                     ST_MakeEnvelope(grid_x, grid_y,
                                     grid_x + :cell_size, grid_y + :cell_size),
                     4326)                                       AS geom,
                   grid_x, grid_y,
                   COUNT(*)                                     AS agent_count,
                   COALESCE(SUM(transactions), 0)               AS total_transactions,
                   COALESCE(SUM(float_balance), 0.0)            AS total_float,
                   ROUND(AVG(float_balance), 2)                 AS avg_float_balance
            FROM pts
            GROUP BY grid_x, grid_y;
        """), {'cell_size': cell_size})
        conn.execute(text(
            f"CREATE INDEX IF NOT EXISTS idx_{table_name}_geom "
            f"ON {table_name} USING GIST (geom);"
        ))
        sql = (f"SELECT grid_x, grid_y, agent_count, total_transactions, "
               f"total_float, avg_float_balance "
               f"FROM {table_name} ORDER BY agent_count DESC LIMIT 50;")
        df = pd.read_sql(text(sql), conn)
    logger.info("Grid summary: %d cells across %.4f°-sized tiles.", len(df), cell_size)
    return df


def ward_agent_summary(limit: int = 1000) -> pd.DataFrame:
    """
    Ward-level agent counts using ``ST_Contains`` spatial join.

    Falls back to ``create_grid_summary`` when ward geometry is absent
    or an error occurs.
    """
    engine = create_engine(DB_URL)
    try:
        with engine.connect() as conn:
            _ensure_postgis(conn)
            df = pd.read_sql(
                text("""
                    SELECT w.ward_name, w.county,
                           COUNT(a.agent_id)        AS agent_count,
                           COALESCE(SUM(a.transactions), 0)   AS total_transactions,
                           COALESCE(SUM(a.float_balance), 0.0) AS total_float,
                           ROUND(AVG(a.float_balance), 2)      AS avg_float_balance
                    FROM wards w
                    LEFT JOIN agents a
                           ON a.geom IS NOT NULL
                           AND ST_Contains(w.geom, a.geom)
                    GROUP BY w.ward_name, w.county
                    ORDER BY agent_count DESC
                    LIMIT :limit;
                """),
                conn,
                params={'limit': limit},
            )
        if df.empty:
            logger.warning("Ward table returned zero rows; falling back to grid summary.")
            return create_grid_summary()
    except Exception as exc:
        logger.warning("Ward join failed (%s); using grid summary.", exc)
        return create_grid_summary()
    return df


def analysis_summary(limit: int = 50                     , grid_cell_size: float = 0.02) -> dict:
    """
    Run all analytics and return a combined summary dictionary.

    Use this in a single DAG step instead of running multiple scripts.
    """
    grid_df  = create_grid_summary(cell_size=grid_cell_size)
    ward_df  = ward_agent_summary(limit=limit)
    summary: dict  = {
        'top_grid_cells':  grid_df.to_dict(orient='records'),
        'top_wards':       ward_df.to_dict(orient='records') if not ward_df.empty else [],
    }
    return summary


if __name__ == '__main__':
    print('Running spatial analytics ...')
    result = analysis_summary(limit=50)
    print(json.dumps(result, indent=2, default=str)[:3000])
    print('[+] Analytics complete.')
