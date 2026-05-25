"""
dags/refresh_daily_dag.py

Enhanced Airflow DAG — nightly M-Pesa agent network data refresh and analytics.

Pipeline
--------
  1. Ingestion              – run cbk_loader.py (CBK data → PostGIS)
  2. Ward aggregates        – build ward_agent_aggregates
  3. Spatial analytics      – ward_analysis.py → agent_density_grid
  4. Export (parallel)      – agents.geojson, wards.geojson, CSV reports
  5. Data-quality checks    – PythonOperator; fails DAG if agents==0 or null_geom>0
  6. Completion log         – append success timestamp to /var/log/airflow/agent_refresh.log

All paths use ``$AIRFLOW_HOME`` rather than hard-coded ``/opt/airflow`` so
the DAG runs unchanged in Docker, docker-compose, and bare-metal Airflow.
"""
import os
from datetime    import datetime, timedelta
from typing     import Any

from sqlalchemy import create_engine, text
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.task_group    import TaskGroup
from airflow.utils.trigger_rule  import TriggerRule
from airflow.utils.email         import send_email

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

AIRFLOW_HOME: str = os.getenv(
    'AIRFLOW_HOME',
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)


def _project_script(*parts: str) -> str:
    """Build a portable absolute path to a project script."""
    return os.path.join(AIRFLOW_HOME, *parts)


# ── Notification callback ────────────────────────────────────────────────────

def _on_failure(context: dict) -> None:  # pragma: no cover
    ti  = context['task_instance']
    msg = (
        f"Airflow DAG '{ti.dag_id}' task '{ti.task_id}' failed.\n"
        f"  Log:   {ti.log_url}\n"
        f"  Try:   {ti.try_number}\n"
        f"  Start: {ti.start_date}"
    )
    try:
        send_email(DEFAULT_ARGS['email'],
                   f"[ALERT] Airflow failure — {ti.dag_id}.{ti.task_id}", msg)
    except Exception as exc:
        logger.warning("Alert email failed: %s", exc)


# ── Quality-check operator ───────────────────────────────────────────────────

logger = __import__('logging').getLogger(__name__)


def _run_quality_checks(**context: Any) -> None:
    """
    Verify post-refresh data health.

    Checks
    ------
    - agents.agent_count  > 0
    - wards.ward_count    > 0
    - agents.null_geom    == 0
    """
    engine = create_engine(os.getenv('MPESA_DATABASE_URL'))
    with engine.connect() as conn:
        agent_count = conn.execute(text('SELECT COUNT(*) FROM agents;')).scalar() or 0
        ward_count  = conn.execute(text('SELECT COUNT(*) FROM wards;')).scalar()   or 0
        null_geom   = conn.execute(
            text('SELECT COUNT(*) FROM agents WHERE geom IS NULL;')
        ).scalar() or 0

        errors: list[str] = []
        if agent_count == 0:
            errors.append(f"No agents found — agent_count={agent_count}")
        if ward_count == 0:
            errors.append(f"No wards found — ward_count={ward_count}")
        if null_geom > 0:
            errors.append(f"{null_geom} agents have NULL geometry.")

        # Push summary metrics so downstream tasks can log them
        for key, val in [('agent_count', agent_count), ('ward_count', ward_count),
                         ('null_geom', null_geom)]:
            context['ti'].xcom_push(key=key, value=val)

        print(f"✓ Agents: {agent_count}, Wards: {ward_count}, Null-geom: {null_geom}")

        if errors:
            raise RuntimeError("Data quality checks FAILED:\n  " + "\n  ".join(errors))


# ── DAG definition ───────────────────────────────────────────────────────────

with DAG(
    dag_id='agent_network_daily_refresh',
    default_args=DEFAULT_ARGS,
    description='Nightly M-Pesa agent network data refresh, analytics, and export.',
    schedule_interval='0 2 * * *',          # 2 AM Nairobi time
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=['mpesa', 'geospatial', 'daily'],
    doc_md="""
Nightly refresh:
1. `extract_load_cbk_data`  — run cbk_loader.py
2. `create_aggregates`     — rebuild ward_agent_aggregates with float metrics
3. `run_spatial_analytics`  — ward_analysis.py → agent_density_grid
4. `export_data` ⧉          — agents.geojson + wards.geojson + CSV reports
5. `data_quality_checks`   — PythonOperator; raises if checks fail
6. `notify_completion`     — append success timestamp toAirflow log
""",
    on_failure_callback=_on_failure,
    timezone='Africa/Nairobi',
    default_args=DEFAULT_ARGS,
) as dag:

    task_extract = BashOperator(
        task_id='extract_load_cbk_data',
        bash_command=f"cd {_project_script()} && python3 ingestion/cbk_loader.py",
        env={**os.environ},
    )

    task_aggregates = BashOperator(
        task_id='create_aggregates',
        bash_command=f"cd {_project_script()} && python3 scripts/create_ward_aggregates.py",
        env={**os.environ},
    )

    task_analytics = BashOperator(
        task_id='run_spatial_analytics',
        bash_command=f"cd {_project_script()} && python3 spatial/ward_analysis.py",
        env={**os.environ},
        execution_timeout=timedelta(minutes=30),
    )

    with TaskGroup('export_data', tooltip='GeoJSON + CSV exports') as export_group:
        task_export_agents = BashOperator(
            task_id='export_agents_geojson',
            bash_command=f"cd {_project_script()} && python3 scripts/export_for_kepler.py",
            env={**os.environ},
            execution_timeout=timedelta(minutes=20),
        )
        task_export_wards = BashOperator(
            task_id='export_wards_geojson',
            bash_command=f"cd {_project_script()} && python3 scripts/export_wards_geojson.py",
            env={**os.environ},
            execution_timeout=timedelta(minutes=20),
        )
        task_export_csv = BashOperator(
            task_id='export_csv_reports',
            bash_command=f"cd {_project_script()} && python3 scripts/export_analysis_csv.py",
            env={**os.environ},
            execution_timeout=timedelta(minutes=20),
        )

    task_quality = PythonOperator(
        task_id='data_quality_checks',
        python_callable=_run_quality_checks,
        trigger_rule=TriggerRule.ALL_SUCCESS,
        execution_timeout=timedelta(minutes=10),
    )

    task_notify = BashOperator(
        task_id='notify_completion',
        bash_command=f'echo "Daily refresh completed at $(date)" >> /var/log/airflow/agent_refresh.log',
        trigger_rule=TriggerRule.ALL_SUCCESS,
    )

    # Defined dependencies: each step must complete before the next.
    # Exports run in parallel after analytics has finished.
    task_extract >> task_aggregates >> task_analytics >> export_group >> task_quality >> task_notify
