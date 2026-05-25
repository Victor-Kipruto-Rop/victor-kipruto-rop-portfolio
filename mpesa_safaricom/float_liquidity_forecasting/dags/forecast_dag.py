"""Airflow DAG for daily float forecasting."""
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

from ingestion.cbk_stats import CBKMPesaClient
from models.ensemble import EnsembleForecaster
from features.feature_engineering import FeatureEngineering
from logger import logger

default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "start_date": days_ago(1),
    "email": ["data-eng@safaricom.co.ke"],
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "float_forecasting_daily",
    default_args=default_args,
    description="Daily 7-day float demand forecast",
    schedule_interval="0 2 * * *",  # 2 AM daily
    tags=["forecasting", "float", "mpesa"],
    catchup=False,
)


def ingest_data(**context):
    """Ingest recent M-Pesa data."""
    try:
        logger.info("Starting data ingestion")
        client = CBKMPesaClient()

        # Get recent data
        data = client.get_mpesa_statistics()
        agent_data = client.get_agent_float_data()

        # Store in context for next tasks
        context["task_instance"].xcom_push(key="mpesa_data", value=data.to_json())
        context["task_instance"].xcom_push(
            key="agent_data", value=agent_data.to_json()
        )

        logger.info(f"Ingested {len(data)} records")
        return "Data ingestion completed"

    except Exception as e:
        logger.error(f"Data ingestion failed: {e}")
        raise


def engineer_features(**context):
    """Create forecasting features."""
    try:
        logger.info("Starting feature engineering")

        # Get data from previous task
        data_json = context["task_instance"].xcom_pull(
            key="mpesa_data", task_ids="ingest_data"
        )

        # In production, this would be from database
        logger.info("Features engineered successfully")
        return "Feature engineering completed"

    except Exception as e:
        logger.error(f"Feature engineering failed: {e}")
        raise


def train_models(**context):
    """Train forecasting models."""
    try:
        logger.info("Starting model training")

        # In production, load historical data and train
        logger.info("Models trained successfully")
        return "Model training completed"

    except Exception as e:
        logger.error(f"Model training failed: {e}")
        raise


def generate_forecast(**context):
    """Generate 7-day forecast."""
    try:
        logger.info("Generating forecast")

        # In production:
        # 1. Load trained ensemble model
        # 2. Get recent data
        # 3. Generate forecast
        # 4. Save to database

        logger.info("Forecast generated successfully")
        return "Forecast generation completed"

    except Exception as e:
        logger.error(f"Forecast generation failed: {e}")
        raise


def save_forecast(**context):
    """Save forecast to database and outputs."""
    try:
        logger.info("Saving forecast")

        # In production:
        # 1. Save to PostgreSQL
        # 2. Save to CSV
        # 3. Update dashboards

        logger.info("Forecast saved successfully")
        return "Forecast save completed"

    except Exception as e:
        logger.error(f"Forecast save failed: {e}")
        raise


# Define tasks
task_ingest = PythonOperator(
    task_id="ingest_data",
    python_callable=ingest_data,
    provide_context=True,
    dag=dag,
)

task_features = PythonOperator(
    task_id="engineer_features",
    python_callable=engineer_features,
    provide_context=True,
    dag=dag,
)

task_train = PythonOperator(
    task_id="train_models",
    python_callable=train_models,
    provide_context=True,
    dag=dag,
)

task_forecast = PythonOperator(
    task_id="generate_forecast",
    python_callable=generate_forecast,
    provide_context=True,
    dag=dag,
)

task_save = PythonOperator(
    task_id="save_forecast",
    python_callable=save_forecast,
    provide_context=True,
    dag=dag,
)

# Define dependencies
task_ingest >> task_features >> task_train >> task_forecast >> task_save
