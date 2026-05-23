"""Facebook Prophet time series forecasting model."""
from datetime import datetime
from typing import Optional, Tuple

import numpy as np
import pandas as pd
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error

from config import settings
from logger import logger


class ProphetForecaster:
    """Prophet-based forecasting model."""

    def __init__(
        self,
        seasonality_mode: str = "additive",
        interval_width: float = 0.95,
        yearly_seasonality: bool = True,
        weekly_seasonality: bool = True,
        daily_seasonality: bool = False,
    ):
        """
        Initialize Prophet forecaster.

        Args:
            seasonality_mode: 'additive' or 'multiplicative'
            interval_width: Confidence interval width
            yearly_seasonality: Include yearly seasonality
            weekly_seasonality: Include weekly seasonality
            daily_seasonality: Include daily seasonality
        """
        self.seasonality_mode = seasonality_mode
        self.interval_width = interval_width
        self.yearly_seasonality = yearly_seasonality
        self.weekly_seasonality = weekly_seasonality
        self.daily_seasonality = daily_seasonality
        self.model = None
        self.training_data = None

    def prepare_data(self, series: pd.Series) -> pd.DataFrame:
        """
        Prepare data for Prophet.

        Args:
            series: Time series data

        Returns:
            DataFrame with 'ds' and 'y' columns
        """
        df = pd.DataFrame({"ds": series.index, "y": series.values})
        df["ds"] = pd.to_datetime(df["ds"])
        return df

    def train(self, series: pd.Series, periods: Optional[int] = None):
        """
        Train Prophet model.

        Args:
            series: Historical time series
            periods: Number of periods used for training
        """
        try:
            if periods:
                series = series.iloc[-periods:]

            self.training_data = self.prepare_data(series)

            self.model = Prophet(
                seasonality_mode=self.seasonality_mode,
                interval_width=self.interval_width,
                yearly_seasonality=self.yearly_seasonality,
                weekly_seasonality=self.weekly_seasonality,
                daily_seasonality=self.daily_seasonality,
                changepoint_prior_scale=0.05,
            )

            self.model.fit(self.training_data)
            logger.info(f"Prophet model trained on {len(self.training_data)} records")

        except Exception as e:
            logger.error(f"Failed to train Prophet model: {e}")
            raise

    def forecast(self, periods: int = 7) -> pd.DataFrame:
        """
        Generate forecast.

        Args:
            periods: Number of periods to forecast

        Returns:
            DataFrame with forecast
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")

        try:
            future = self.model.make_future_dataframe(periods=periods)
            forecast = self.model.predict(future)

            logger.info(f"Generated {periods}-period forecast")
            return forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(
                periods
            )

        except Exception as e:
            logger.error(f"Forecast generation failed: {e}")
            raise

    def evaluate(self, test_series: pd.Series) -> dict:
        """
        Evaluate model on test data.

        Args:
            test_series: Test time series

        Returns:
            Dictionary with metrics
        """
        if self.model is None:
            raise ValueError("Model not trained.")

        try:
            test_df = self.prepare_data(test_series)
            forecast = self.model.predict(test_df[["ds"]])

            y_true = test_df["y"].values
            y_pred = forecast["yhat"].values

            mae = mean_absolute_error(y_true, y_pred)
            rmse = np.sqrt(mean_squared_error(y_true, y_pred))
            mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100

            metrics = {"MAE": mae, "RMSE": rmse, "MAPE": mape}
            logger.info(f"Evaluation metrics: {metrics}")

            return metrics

        except Exception as e:
            logger.error(f"Model evaluation failed: {e}")
            raise

    def add_regressors(
        self, regressor_df: pd.DataFrame, regressor_names: list[str]
    ):
        """
        Add external regressors to model.

        Args:
            regressor_df: DataFrame with regressors
            regressor_names: List of regressor column names
        """
        if self.model is None:
            raise ValueError("Model not trained yet.")

        for regressor in regressor_names:
            if regressor not in regressor_df.columns:
                logger.warning(f"Regressor {regressor} not found")
                continue
            self.model.add_regressor(regressor)

        logger.info(f"Added {len(regressor_names)} regressors to model")

    def get_components(self) -> Optional[pd.DataFrame]:
        """
        Get model components (trend, seasonality, etc.).

        Returns:
            DataFrame with components
        """
        if self.model is None:
            return None

        components = self.model.plot_components(make_subplots=True)
        logger.info("Retrieved model components")
        return components

    def save_model(self, path: str):
        """Save model to disk."""
        if self.model is None:
            raise ValueError("Model not trained.")

        import pickle

        with open(path, "wb") as f:
            pickle.dump(self.model, f)
        logger.info(f"Model saved to {path}")

    def load_model(self, path: str):
        """Load model from disk."""
        import pickle

        with open(path, "rb") as f:
            self.model = pickle.load(f)
        logger.info(f"Model loaded from {path}")
