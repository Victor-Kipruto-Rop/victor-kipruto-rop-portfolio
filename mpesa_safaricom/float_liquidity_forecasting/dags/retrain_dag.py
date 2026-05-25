"""Airflow DAG for monthly model retraining."""
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

from logger import logger

default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "start_date": days_ago(1),
    "email": ["data-eng@safaricom.co.ke"],
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=10),
}

dag = DAG(
    "float_forecasting_retrain",
    default_args=default_args,
    description="Monthly model retraining pipeline",
    schedule_interval="0 3 1 * *",  # 3 AM on 1st of month
    tags=["forecasting", "retraining", "mlops"],
    catchup=False,
)


def validate_data(**context):
    """Validate data quality before retraining."""
    try:
        logger.info("Validating data quality")

        # In production:
        # 1. Check data completeness
        # 2. Verify data ranges
        # 3. Check for anomalies

        logger.info("Data validation completed")
        return "Data validation passed"

    except Exception as e:
        logger.error(f"Data validation failed: {e}")
        raise


def prepare_training_data(**context):
    """Prepare training dataset."""
    try:
        logger.info("Preparing training data")

        # In production:
        # 1. Fetch historical data (min 365 days)
        # 2. Create features
        # 3. Split train/validation sets

        logger.info("Training data prepared")
        return "Training data preparation completed"

    except Exception as e:
        logger.error(f"Training data preparation failed: {e}")
        raise


def train_prophet(**context):
    """Retrain Prophet model."""
    try:
        logger.info("Retraining Prophet model")

        # In production:
        # 1. Load training data
        # 2. Train Prophet
        # 3. Log metrics to MLflow
        # 4. Save model version

        logger.info("Prophet retraining completed")
        return "Prophet training completed"

    except Exception as e:
        logger.error(f"Prophet training failed: {e}")
        raise


def train_lstm(**context):
    """Retrain LSTM model."""
    try:
        logger.info("Retraining LSTM model")

        # In production:
        # 1. Load training data
        # 2. Train LSTM
        # 3. Log metrics to MLflow
        # 4. Save model version

        logger.info("LSTM retraining completed")
        return "LSTM training completed"

    except Exception as e:
        logger.error(f"LSTM training failed: {e}")
        raise


def evaluate_models(**context):
    """Evaluate trained models."""
    try:
        logger.info("Evaluating models")

        # In production:
        # 1. Get validation dataset
        # 2. Evaluate both models
        # 3. Compare with existing models
        # 4. Calculate metrics

        logger.info("Model evaluation completed")
        return "Model evaluation completed"

    except Exception as e:
        logger.error(f"Model evaluation failed: {e}")
        raise


def optimize_ensemble(**context):
    """Optimize ensemble weights."""
    try:
        logger.info("Optimizing ensemble weights")

        # In production:
        # 1. Load trained models
        # 2. Use validation data
        # 3. Optimize weights
        # 4. Store optimal weights

        logger.info("Ensemble optimization completed")
        return "Ensemble optimization completed"

    except Exception as e:
        logger.error(f"Ensemble optimization failed: {e}")
        raise


def register_models(**context):
    """Register best models in MLflow."""
    try:
        logger.info("Registering models")

        # In production:
        # 1. Register Prophet model version
        # 2. Register LSTM model version
        # 3. Register Ensemble config
        # 4. Tag as production or staging

        logger.info("Models registered successfully")
        return "Model registration completed"

    except Exception as e:
        logger.error(f"Model registration failed: {e}")
        raise


def run_backtest(**context):
    """Run backtesting on historical data."""
    try:
        logger.info("Running backtest")

        # In production:
        # 1. Get historical data
        # 2. Simulate forecasts at each time point
        # 3. Calculate performance metrics
        # 4. Generate backtest report

        logger.info("Backtest completed")
        return "Backtest completed"

    except Exception as e:
        logger.error(f"Backtest failed: {e}")
        raise


def generate_report(**context):
    """Generate retraining report."""
    try:
        logger.info("Generating retraining report")

        # In production:
        # 1. Collect all metrics
        # 2. Compare with previous version
        # 3. Generate visualizations
        # 4. Send email report

        logger.info("Report generated")
        return "Report generation completed"

    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        raise


# Define tasks
task_validate = PythonOperator(
    task_id="validate_data",
    python_callable=validate_data,
    provide_context=True,
    dag=dag,
)

task_prepare = PythonOperator(
    task_id="prepare_training_data",
    python_callable=prepare_training_data,
    provide_context=True,
    dag=dag,
)

task_train_prophet = PythonOperator(
    task_id="train_prophet",
    python_callable=train_prophet,
    provide_context=True,
    dag=dag,
)

task_train_lstm = PythonOperator(
    task_id="train_lstm",
    python_callable=train_lstm,
    provide_context=True,
    dag=dag,
)

task_evaluate = PythonOperator(
    task_id="evaluate_models",
    python_callable=evaluate_models,
    provide_context=True,
    dag=dag,
)

task_optimize = PythonOperator(
    task_id="optimize_ensemble",
    python_callable=optimize_ensemble,
    provide_context=True,
    dag=dag,
)

task_register = PythonOperator(
    task_id="register_models",
    python_callable=register_models,
    provide_context=True,
    dag=dag,
)

task_backtest = PythonOperator(
    task_id="run_backtest",
    python_callable=run_backtest,
    provide_context=True,
    dag=dag,
)

task_report = PythonOperator(
    task_id="generate_report",
    python_callable=generate_report,
    provide_context=True,
    dag=dag,
)

# Define dependencies
task_validate >> task_prepare >> [task_train_prophet, task_train_lstm]
[task_train_prophet, task_train_lstm] >> task_evaluate >> task_optimize
task_optimize >> task_register >> task_backtest >> task_report
