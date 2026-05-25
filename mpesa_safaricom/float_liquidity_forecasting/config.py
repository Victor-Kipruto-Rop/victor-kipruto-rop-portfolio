"""Configuration management for Float Liquidity Forecasting project."""
import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Project paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent
    DATA_DIR: Path = PROJECT_ROOT / "data"
    MODELS_DIR: Path = PROJECT_ROOT / "models"
    OUTPUTS_DIR: Path = PROJECT_ROOT / "outputs"
    LOGS_DIR: Path = PROJECT_ROOT / "logs"

    # Database
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "float_forecasting")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "password")
    DATABASE_URL: str = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    # MLflow
    MLFLOW_TRACKING_URI: str = os.getenv(
        "MLFLOW_TRACKING_URI", "http://localhost:5000"
    )
    MLFLOW_EXPERIMENT_NAME: str = "float-forecasting"

    # Airflow
    AIRFLOW_HOME: str = os.getenv("AIRFLOW_HOME", str(PROJECT_ROOT / "airflow"))
    AIRFLOW_DAG_FOLDER: Path = PROJECT_ROOT / "dags"

    # Forecasting
    FORECAST_HORIZON: int = 7  # days ahead
    RETRAIN_INTERVAL: int = 30  # days between retraining
    MIN_HISTORICAL_DATA: int = 365  # days required for training
    CONFIDENCE_LEVEL: float = 0.95

    # Models
    PROPHET_SEASONALITY_MODE: str = "additive"
    PROPHET_INTERVAL_WIDTH: float = 0.95
    LSTM_UNITS: int = 64
    LSTM_DROPOUT: float = 0.2
    LSTM_BATCH_SIZE: int = 32
    LSTM_EPOCHS: int = 50
    LSTM_VALIDATION_SPLIT: float = 0.1

    # Feature Engineering
    LAG_PERIODS: list[int] = [1, 7, 30]
    ROLLING_WINDOW_SIZES: list[int] = [7, 14, 30]

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = (
        "<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:"
        "<cyan>{line}</cyan> - <level>{message}</level>"
    )

    # External APIs
    CBK_API_URL: Optional[str] = os.getenv("CBK_API_URL", None)
    HOLIDAYS_API_URL: str = "https://date.nager.at/api/v3"
    COUNTRY_CODE: str = "KE"

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development"

    class Config:
        """Pydantic config."""

        env_file = ".env"
        env_file_encoding = "utf-8"


# Create settings instance
settings = Settings()

# Create necessary directories
settings.DATA_DIR.mkdir(exist_ok=True)
settings.MODELS_DIR.mkdir(exist_ok=True)
settings.OUTPUTS_DIR.mkdir(exist_ok=True)
settings.LOGS_DIR.mkdir(exist_ok=True)
