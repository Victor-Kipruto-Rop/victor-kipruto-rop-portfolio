"""Ensemble forecasting combining multiple models."""
from typing import Optional

import numpy as np
import pandas as pd

from logger import logger
from models.lstm_model import LSTMForecaster
from models.prophet_model import ProphetForecaster


class EnsembleForecaster:
    """Combine Prophet and LSTM models for improved forecasting."""

    def __init__(
        self,
        prophet_weight: float = 0.5,
        lstm_weight: float = 0.5,
    ):
        """
        Initialize ensemble forecaster.

        Args:
            prophet_weight: Weight for Prophet model
            lstm_weight: Weight for LSTM model
        """
        self.prophet_weight = prophet_weight
        self.lstm_weight = lstm_weight

        # Normalize weights
        total_weight = prophet_weight + lstm_weight
        self.prophet_weight /= total_weight
        self.lstm_weight /= total_weight

        self.prophet_model = ProphetForecaster()
        self.lstm_model = LSTMForecaster()

        logger.info(
            f"Ensemble initialized with Prophet weight={self.prophet_weight:.2f}, "
            f"LSTM weight={self.lstm_weight:.2f}"
        )

    def train(self, series: pd.Series, verbose: int = 0):
        """
        Train both models.

        Args:
            series: Historical time series
            verbose: Verbosity level
        """
        try:
            logger.info("Training Prophet model...")
            self.prophet_model.train(series)

            logger.info("Training LSTM model...")
            self.lstm_model.train(series, verbose=verbose)

            logger.info("Ensemble training completed")

        except Exception as e:
            logger.error(f"Ensemble training failed: {e}")
            raise

    def forecast(self, series: pd.Series, periods: int = 7) -> dict:
        """
        Generate ensemble forecast.

        Args:
            series: Recent history
            periods: Number of periods to forecast

        Returns:
            Dictionary with ensemble forecast and individual models
        """
        try:
            # Get individual forecasts
            prophet_forecast = self.prophet_model.forecast(periods)
            lstm_forecast = self.lstm_model.forecast(series, periods)

            # Extract point estimates
            prophet_values = prophet_forecast["yhat"].values
            lstm_values = lstm_forecast

            # Ensemble forecast
            ensemble_forecast = (
                self.prophet_weight * prophet_values
                + self.lstm_weight * lstm_values
            )

            # Get confidence intervals from Prophet
            lower = prophet_forecast["yhat_lower"].values
            upper = prophet_forecast["yhat_upper"].values

            result = {
                "ensemble": ensemble_forecast,
                "prophet": prophet_values,
                "lstm": lstm_values,
                "lower": lower,
                "upper": upper,
                "dates": prophet_forecast["ds"].values,
            }

            logger.info(f"Generated ensemble forecast for {periods} periods")
            return result

        except Exception as e:
            logger.error(f"Ensemble forecast failed: {e}")
            raise

    def evaluate(self, test_series: pd.Series) -> dict:
        """
        Evaluate ensemble and individual models.

        Args:
            test_series: Test time series

        Returns:
            Dictionary with evaluation metrics
        """
        try:
            prophet_metrics = self.prophet_model.evaluate(test_series)
            lstm_metrics = self.lstm_model.evaluate(test_series)

            metrics = {
                "prophet": prophet_metrics,
                "lstm": lstm_metrics,
            }

            logger.info(f"Ensemble evaluation: {metrics}")
            return metrics

        except Exception as e:
            logger.error(f"Ensemble evaluation failed: {e}")
            raise

    def update_weights(self, prophet_weight: float, lstm_weight: float):
        """
        Update model weights.

        Args:
            prophet_weight: New weight for Prophet
            lstm_weight: New weight for LSTM
        """
        total = prophet_weight + lstm_weight
        self.prophet_weight = prophet_weight / total
        self.lstm_weight = lstm_weight / total

        logger.info(
            f"Ensemble weights updated: Prophet={self.prophet_weight:.2f}, "
            f"LSTM={self.lstm_weight:.2f}"
        )

    def optimize_weights(
        self, validation_series: pd.Series, n_iterations: int = 20
    ):
        """
        Optimize ensemble weights using validation data.

        Args:
            validation_series: Validation time series
            n_iterations: Number of weight combinations to try
        """
        try:
            from sklearn.metrics import mean_absolute_error

            best_mae = float("inf")
            best_weights = (0.5, 0.5)

            for prophet_w in np.linspace(0.1, 0.9, n_iterations):
                lstm_w = 1.0 - prophet_w

                self.update_weights(prophet_w, lstm_w)
                forecast = self.forecast(validation_series)
                ensemble_values = forecast["ensemble"]

                mae = mean_absolute_error(
                    validation_series.values[-len(ensemble_values) :],
                    ensemble_values,
                )

                if mae < best_mae:
                    best_mae = mae
                    best_weights = (prophet_w, lstm_w)

            self.update_weights(best_weights[0], best_weights[1])
            logger.info(f"Optimal weights found: {best_weights}, MAE={best_mae:.2f}")

        except Exception as e:
            logger.error(f"Weight optimization failed: {e}")
            raise
