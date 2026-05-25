"""
dags/ingest_cbk_dag.py

Airflow DAG: ingest CBK agent-banking data.

Pipeline
--------
1. extract_pdfs   – download CBK PDF files and run pdf_extractor.py
2. load_to_postgis – run cbk_loader.py to upsert agents into PostGIS

The DAG is self-documenting via a doc-string and has email-on-failure
notifications.  All paths use ``$AIRFLOW_HOME`` so the DAG is portable
across Docker, compose, and bare-metal Airflow installs.
"""

import os
import sys
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.trigger_rule    import TriggerRule
from airflow.utils.email   import send_email

# ── Default args ─────────────────────────────────────────────────────────────

DEFAULT_ARGS = {
    'owner':           'data-engineering',
    'depends_on_past': False,
    'email':           ['data-alerts@company.com'],
    'email_on_failure': True,
    'email_on_retry':  False,
    'retries':         2,
    'retry_delay':     timedelta(minutes=5),
    'retry_exponential_backoff': True,
}

# ── Airflow home helpers ─────────────────────────────────────────────────────

AIRFLOW_HOME: str = os.getenv('AIRFLOW_HOME', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _script_path(*parts: str) -> str:
    """Return an absolute path to a project script, using $AIRFLOW_HOME."""
    return os.path.join(AIRFLOW_HOME, 'ingestion', *parts) \
        if parts[0] in ('ingestion',) else \
        os.path.join(AIRFLOW_HOME, *parts)


# ── Notification callback ────────────────────────────────────────────────────

def _on_failure(context: dict) -> None:  # pragma: no cover
    """Send a concise alert email on task failure."""
    ti  = context['task_instance']
    msg = (
        f"Airflow DAG '{ti.dag_id}' task '{ti.task_id}' failed.\n"
        f"  Log:   {ti.log_url}\n"
        f"  Try:   {ti.try_number}\n"
        f"  Start: {ti.start_date}"
    )
    try:
        send_email(DEFAULT_ARGS['email'], f"[ALERT] Airflow failure — {ti.dag_id}.{ti.task_id}", msg)
    except Exception as exc:
        logger.warning("Alert email failed: %s", exc)


def _quality_check(**context) -> None:
    """
    Run post-ingestion sanity checks via PythonOperator so failures
    surface as a failed task (not a silent bash exit code).
    """
    from sqlalchemy import create_engine, text

    engine = create_engine(os.getenv('MPESA_DATABASE_URL'))
    with engine.connect() as conn:
        agent_count = conn.execute(text('SELECT COUNT(*) FROM agents;')).scalar() or 0
        null_geom   = conn.execute(text('SELECT COUNT(*) FROM agents WHERE geom IS NULL;')).scalar() or 0
        errors: list[str] = []

        if agent_count == 0:
            errors.append("No agents found in the agents table.")
        if null_geom > 0:
            errors.append(f"{null_geom} agents have a NULL geometry.")

        if errors:
            raise RuntimeError("Data quality checks failed:\n  " + "\n  ".join(errors))


# ── DAG definition ───────────────────────────────────────────────────────────

with DAG(
    dag_id='ingest_cbk',
    default_args=DEFAULT_ARGS,
    description='Download CBK agent-banking PDFs and load agents into PostGIS.',
    schedule_interval=None,          # manually triggered; set '@daily' in prod
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=['mpesa', 'ingestion'],
    doc_md="""Ingestion DAG:
1. extract_pdfs — runs pdf_extractor.py to pull tables from CBK PDFs
2. load_to_postgis — upserts the resulting CSV/Excel files into PostGIS
""",
    on_failure_callback=_on_failure,
    timezone='Africa/Nairobi',
) as dag:

    extract_pdfs = BashOperator(
        task_id='extract_pdfs',
        bash_command=f"cd {AIRFLOW_HOME} && python3 ingestion/pdf_extractor.py",
        env={**os.environ},
    )

    load_to_postgis = BashOperator(
        task_id='load_to_postgis',
        bash_command=f"cd {AIRFLOW_HOME} && python3 ingestion/cbk_loader.py",
        env={**os.environ},
    )

    post_ingest_quality = PythonOperator(
        task_id='post_ingest_quality_check',
        python_callable=_quality_check,
        trigger_rule=TriggerRule.ALL_SUCCESS,
    )

    extract_pdfs >> load_to_postgis >> post_ingest_quality
