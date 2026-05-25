"""Feature engineering for time series forecasting."""
from typing import Optional

import numpy as np
import pandas as pd
from scipy import stats

from config import settings
from logger import logger


class FeatureEngineering:
    """Time series feature engineering."""

    def __init__(
        self,
        lag_periods: Optional[list[int]] = None,
        rolling_windows: Optional[list[int]] = None,
    ):
        """
        Initialize feature engineering.

        Args:
            lag_periods: Lag periods to create
            rolling_windows: Rolling window sizes
        """
        self.lag_periods = lag_periods or settings.LAG_PERIODS
        self.rolling_windows = rolling_windows or settings.ROLLING_WINDOW_SIZES

    def create_lagged_features(
        self, series: pd.Series, periods: Optional[list[int]] = None
    ) -> pd.DataFrame:
        """
        Create lagged features.

        Args:
            series: Input time series
            periods: Lag periods

        Returns:
            DataFrame with lagged features
        """
        periods = periods or self.lag_periods
        df = pd.DataFrame({"target": series})

        for period in periods:
            df[f"lag_{period}"] = series.shift(period)

        logger.info(f"Created {len(periods)} lagged features")
        return df

    def create_rolling_features(
        self, series: pd.Series, windows: Optional[list[int]] = None
    ) -> pd.DataFrame:
        """
        Create rolling window features.

        Args:
            series: Input time series
            windows: Window sizes

        Returns:
            DataFrame with rolling features
        """
        windows = windows or self.rolling_windows
        df = pd.DataFrame({"target": series})

        for window in windows:
            df[f"rolling_mean_{window}"] = series.rolling(window).mean()
            df[f"rolling_std_{window}"] = series.rolling(window).std()
            df[f"rolling_min_{window}"] = series.rolling(window).min()
            df[f"rolling_max_{window}"] = series.rolling(window).max()

        logger.info(f"Created rolling features for {len(windows)} windows")
        return df

    def create_seasonal_features(self, dates: pd.DatetimeIndex) -> pd.DataFrame:
        """
        Create temporal/seasonal features.

        Args:
            dates: DateTime index

        Returns:
            DataFrame with seasonal features
        """
        df = pd.DataFrame(index=dates)

        # Date features
        df["day_of_week"] = dates.dayofweek
        df["day_of_month"] = dates.day
        df["month"] = dates.month
        df["quarter"] = dates.quarter
        df["day_of_year"] = dates.dayofyear
        df["week_of_year"] = dates.isocalendar().week

        # Cyclical features (convert to sin/cos for better ML)
        df["day_sin"] = np.sin(2 * np.pi * df["day_of_week"] / 7)
        df["day_cos"] = np.cos(2 * np.pi * df["day_of_week"] / 7)
        df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
        df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)

        # Business day indicator
        df["is_business_day"] = dates.dayofweek < 5

        logger.info("Created seasonal features")
        return df

    def create_trend_features(self, series: pd.Series) -> pd.DataFrame:
        """
        Create trend features.

        Args:
            series: Input time series

        Returns:
            DataFrame with trend features
        """
        df = pd.DataFrame({"target": series})

        # Linear trend
        x = np.arange(len(series))
        slope, intercept, _, _, _ = stats.linregress(x, series.values)
        df["trend"] = x * slope + intercept

        # Differencing (change from previous)
        df["diff_1"] = series.diff()
        df["diff_7"] = series.diff(7)

        # Growth rate
        df["growth_rate"] = series.pct_change()

        logger.info("Created trend features")
        return df

    def create_all_features(
        self, series: pd.Series, dates: pd.DatetimeIndex
    ) -> pd.DataFrame:
        """
        Create all features combined.

        Args:
            series: Input time series
            dates: DateTime index

        Returns:
            Combined DataFrame with all features
        """
        df = pd.DataFrame({"target": series}, index=dates)

        # Add all feature types
        lagged = self.create_lagged_features(series)
        rolling = self.create_rolling_features(series)
        seasonal = self.create_seasonal_features(dates)
        trend = self.create_trend_features(series)

        # Combine all features
        for col in lagged.columns:
            if col != "target":
                df[col] = lagged[col]
        for col in rolling.columns:
            if col != "target":
                df[col] = rolling[col]
        for col in seasonal.columns:
            df[col] = seasonal[col]
        for col in trend.columns:
            if col != "target":
                df[col] = trend[col]

        # Drop rows with NaN (from lagging/rolling)
        df = df.dropna()

        logger.info(f"Created {len(df.columns)} features")
        return df

    @staticmethod
    def normalize_features(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
        """
        Normalize features using z-score normalization.

        Args:
            df: Input DataFrame

        Returns:
            Normalized DataFrame and scaling parameters
        """
        scaling_params = {}
        df_normalized = df.copy()

        for col in df.columns:
            if col != "target":
                mean = df[col].mean()
                std = df[col].std()
                scaling_params[col] = {"mean": mean, "std": std}
                df_normalized[col] = (df[col] - mean) / (std + 1e-8)

        logger.info(f"Normalized {len(df.columns)} features")
        return df_normalized, scaling_params

    @staticmethod
    def handle_outliers(series: pd.Series, method: str = "iqr") -> pd.Series:
        """
        Handle outliers in time series.

        Args:
            series: Input series
            method: 'iqr' or 'zscore'

        Returns:
            Series with outliers handled
        """
        series_cleaned = series.copy()

        if method == "iqr":
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            series_cleaned = series.clip(lower_bound, upper_bound)

        elif method == "zscore":
            z_scores = np.abs(stats.zscore(series))
            series_cleaned[z_scores > 3] = series.mean()

        logger.info(f"Handled outliers using {method} method")
        return series_cleaned
