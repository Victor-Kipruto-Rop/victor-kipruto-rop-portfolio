"""Model evaluation and metrics calculation."""
from typing import Optional

import numpy as np
import pandas as pd
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    mean_absolute_percentage_error,
    median_absolute_error,
)

from logger import logger


class ModelEvaluator:
    """Comprehensive model evaluation."""

    @staticmethod
    def calculate_mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Mean Absolute Error."""
        return mean_absolute_error(y_true, y_pred)

    @staticmethod
    def calculate_rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Root Mean Squared Error."""
        return np.sqrt(mean_squared_error(y_true, y_pred))

    @staticmethod
    def calculate_mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Mean Absolute Percentage Error."""
        return mean_absolute_percentage_error(y_true, y_pred) * 100

    @staticmethod
    def calculate_median_ae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Median Absolute Error."""
        return median_absolute_error(y_true, y_pred)

    @staticmethod
    def calculate_smape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Symmetric Mean Absolute Percentage Error."""
        denominator = (np.abs(y_true) + np.abs(y_pred)) / 2.0
        diff = np.abs(y_true - y_pred) / denominator
        diff[denominator == 0] = 0
        return 100.0 * np.mean(diff)

    @staticmethod
    def calculate_directional_accuracy(
        y_true: np.ndarray, y_pred: np.ndarray
    ) -> float:
        """
        Directional Accuracy - percentage of correct directional predictions.
        """
        true_direction = np.diff(y_true) > 0
        pred_direction = np.diff(y_pred) > 0
        correct = (true_direction == pred_direction).sum()
        return (correct / len(true_direction)) * 100

    @staticmethod
    def calculate_theil_u(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Theil's U statistic - asymmetric accuracy measure."""
        numerator = np.sum((y_true - y_pred) ** 2)
        denominator = np.sum(y_true**2) + np.sum(y_pred**2)
        return np.sqrt(numerator / denominator)

    @staticmethod
    def get_all_metrics(
        y_true: np.ndarray, y_pred: np.ndarray
    ) -> dict:
        """
        Calculate all evaluation metrics.

        Args:
            y_true: True values
            y_pred: Predicted values

        Returns:
            Dictionary with all metrics
        """
        metrics = {
            "MAE": ModelEvaluator.calculate_mae(y_true, y_pred),
            "RMSE": ModelEvaluator.calculate_rmse(y_true, y_pred),
            "MAPE": ModelEvaluator.calculate_mape(y_true, y_pred),
            "MedianAE": ModelEvaluator.calculate_median_ae(y_true, y_pred),
            "SMAPE": ModelEvaluator.calculate_smape(y_true, y_pred),
            "DirectionalAccuracy": ModelEvaluator.calculate_directional_accuracy(
                y_true, y_pred
            ),
            "TheilU": ModelEvaluator.calculate_theil_u(y_true, y_pred),
        }

        return metrics

    @staticmethod
    def evaluate_forecast(
        forecast_df: pd.DataFrame,
        actual_series: pd.Series,
        forecast_col: str = "yhat",
    ) -> dict:
        """
        Evaluate forecast against actual values.

        Args:
            forecast_df: DataFrame with forecast
            actual_series: Actual time series
            forecast_col: Column name with forecasts

        Returns:
            Dictionary with metrics
        """
        # Align dates
        forecast_dates = forecast_df["ds"].dt.date
        actual_dates = actual_series.index.date

        # Find matching dates
        matching_indices = []
        for i, fdate in enumerate(forecast_dates):
            matches = np.where(actual_dates == fdate)[0]
            if len(matches) > 0:
                matching_indices.append((i, matches[0]))

        if not matching_indices:
            logger.warning("No matching dates between forecast and actual")
            return {}

        # Extract matching values
        forecast_indices, actual_indices = zip(*matching_indices)
        y_pred = forecast_df.iloc[list(forecast_indices)][forecast_col].values
        y_true = actual_series.iloc[list(actual_indices)].values

        metrics = ModelEvaluator.get_all_metrics(y_true, y_pred)
        logger.info(f"Forecast evaluation metrics: {metrics}")

        return metrics

    @staticmethod
    def calculate_confidence_interval(
        predictions: np.ndarray,
        confidence: float = 0.95,
        method: str = "std",
    ) -> tuple:
        """
        Calculate confidence intervals.

        Args:
            predictions: Forecast values
            confidence: Confidence level (0-1)
            method: 'std' for standard deviation or 'quantile'

        Returns:
            Tuple of (lower, upper) bounds
        """
        if method == "std":
            std_dev = np.std(predictions)
            margin = std_dev * (1 - confidence) / 2
            lower = predictions - margin
            upper = predictions + margin
        else:
            alpha = (1 - confidence) / 2
            lower = np.quantile(predictions, alpha)
            upper = np.quantile(predictions, 1 - alpha)

        return lower, upper

    @staticmethod
    def calculate_residuals(
        y_true: np.ndarray, y_pred: np.ndarray
    ) -> dict:
        """
        Analyze residuals.

        Args:
            y_true: True values
            y_pred: Predictions

        Returns:
            Dictionary with residual statistics
        """
        residuals = y_true - y_pred

        stats = {
            "mean": np.mean(residuals),
            "std": np.std(residuals),
            "min": np.min(residuals),
            "max": np.max(residuals),
            "median": np.median(residuals),
            "skewness": (
                np.mean(residuals**3) / (np.std(residuals) ** 3)
                if np.std(residuals) > 0
                else 0
            ),
        }

        return stats
