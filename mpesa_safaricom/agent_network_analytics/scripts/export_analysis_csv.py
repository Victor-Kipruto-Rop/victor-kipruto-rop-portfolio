"""
export_analysis_csv.py

Export analysis results and summaries to CSV for charting and reporting.

Exports
-------
 ward_summary.csv       ward_agent_aggregates (all rows)
 grid_density.csv       agent_density_grid  (grid_x, grid_y, agent_count, total_transactions, total_float)
 top_agents.csv         agents ordered by transactions desc (limit 1 000)
 county_summary.csv     agent counts + transaction totals by county
"""
import os
import logging
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_URL  = os.getenv('MPESA_DATABASE_URL', 'postgresql://mpesa:mpesa_pass@localhost:5433/mpesa')
OUT_DIR: Path = Path(__file__).resolve().parents[1] / 'data' / 'reports'


def export_all(base_dir: str | Path | None = None) -> dict[str, Path]:
    out = Path(base_dir) if base_dir else OUT_DIR
    out.mkdir(parents=True, exist_ok=True)
    engine = create_engine(DB_URL)
    written: dict[str, Path] = {}

    # 1. Ward summary (with float metrics)
    ward_cols = ('ward_code, ward_name, county, agent_count, total_transactions, '
                 'total_float, avg_float_balance, float_util_ratio, float_below_threshold')
    try:
        df_wards = pd.read_sql(
            text(f"SELECT {ward_cols} FROM ward_agent_aggregates ORDER BY agent_count DESC;"),
            engine,
        )
        path = out / 'ward_summary.csv'
        df_wards.to_csv(path, index=False)
        written['ward_summary'] = path
        logger.info("✓ Exported ward summary (%d rows) → %s", len(df_wards), path)
    except Exception as exc:
        logger.error("× Ward summary export failed: %s", exc)

    # 2. Grid density summary
    grid_cols = ('grid_x, grid_y, agent_count, total_transactions, total_float, avg_float_balance')
    try:
        df_grid = pd.read_sql(
            text(f"SELECT {grid_cols} FROM agent_density_grid ORDER BY agent_count DESC;"),
            engine,
        )
        path = out / 'grid_density.csv'
        df_grid.to_csv(path, index=False)
        written['grid_density'] = path
        logger.info("✓ Exported grid density (%d rows) → %s", len(df_grid), path)
    except Exception as exc:
        logger.error("× Grid density export failed: %s", exc)

    # 3. Top agents
    try:
        with engine.connect() as conn:
            df_agents = pd.read_sql(
                text(
                    "SELECT agent_id, agent_name, county, ward, "
                    "       transactions, total_transaction_amount, float_balance "
                    "FROM agents ORDER BY transactions DESC LIMIT 1000;"
                ), conn)
        path = out / 'top_agents.csv'
        df_agents.to_csv(path, index=False)
        written['top_agents'] = path
        logger.info("✓ Exported top agents (%d rows) → %s", len(df_agents), path)
    except Exception as exc:
        logger.error("× Top agents export failed: %s", exc)

    # 4. County summary
    try:
        with engine.connect() as conn:
            df_county = pd.read_sql(
                text(
                    "SELECT county, COUNT(*) AS agent_count, "
                    "       SUM(transactions)      AS total_transactions, "
                    "       SUM(float_balance)     AS total_float, "
                    "       ROUND(AVG(float_balance), 2) AS avg_float_balance "
                    "FROM agents GROUP BY county ORDER BY agent_count DESC;"
                ), conn)
        path = out / 'county_summary.csv'
        df_county.to_csv(path, index=False)
        written['county_summary'] = path
        logger.info("✓ Exported county summary (%d rows) → %s", len(df_county), path)
    except Exception as exc:
        logger.error("× County summary export failed: %s", exc)

    logger.info("All CSVs written to %s", out)
    return written


if __name__ == '__main__':
    export_all()
