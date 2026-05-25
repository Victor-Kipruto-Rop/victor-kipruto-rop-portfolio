"""Tests for feature engineering module."""
import pytest
import pandas as pd
import numpy as np

from features.feature_engineering import FeatureEngineering


class TestFeatureEngineering:
    """Test feature engineering functionality."""

    @pytest.fixture
    def fe(self):
        """Create FeatureEngineering instance."""
        return FeatureEngineering(lag_periods=[1, 7], rolling_windows=[7, 14])

    @pytest.fixture
    def sample_series(self):
        """Create sample time series."""
        dates = pd.date_range("2023-01-01", periods=100)
        data = np.random.randn(100).cumsum() + 100
        return pd.Series(data, index=dates)

    def test_create_lagged_features(self, fe, sample_series):
        """Test lagged feature creation."""
        df = fe.create_lagged_features(sample_series)
        
        assert "lag_1" in df.columns
        assert "lag_7" in df.columns
        assert len(df) == len(sample_series)

    def test_create_rolling_features(self, fe, sample_series):
        """Test rolling feature creation."""
        df = fe.create_rolling_features(sample_series)
        
        assert "rolling_mean_7" in df.columns
        assert "rolling_std_7" in df.columns
        assert "rolling_min_14" in df.columns
        assert "rolling_max_14" in df.columns

    def test_create_seasonal_features(self, fe, sample_series):
        """Test seasonal feature creation."""
        df = fe.create_seasonal_features(sample_series.index)
        
        assert "day_of_week" in df.columns
        assert "month" in df.columns
        assert "day_sin" in df.columns
        assert "is_business_day" in df.columns

    def test_create_trend_features(self, fe, sample_series):
        """Test trend feature creation."""
        df = fe.create_trend_features(sample_series)
        
        assert "trend" in df.columns
        assert "diff_1" in df.columns
        assert "growth_rate" in df.columns

    def test_normalize_features(self, sample_series):
        """Test feature normalization."""
        df = pd.DataFrame({
            "feature1": sample_series,
            "feature2": sample_series * 2,
        })
        
        normalized, params = FeatureEngineering.normalize_features(df)
        
        assert np.abs(normalized["feature1"].mean()) < 0.01
        assert np.abs(normalized["feature1"].std() - 1.0) < 0.01
        assert "feature1" in params
        assert "feature2" in params

    def test_handle_outliers_iqr(self, sample_series):
        """Test IQR outlier handling."""
        # Add outliers
        series_with_outliers = sample_series.copy()
        series_with_outliers.iloc[0] = 1000
        series_with_outliers.iloc[1] = -1000
        
        cleaned = FeatureEngineering.handle_outliers(
            series_with_outliers, method="iqr"
        )
        
        assert cleaned.iloc[0] != 1000
        assert cleaned.iloc[1] != -1000

    def test_all_features(self, fe, sample_series):
        """Test combined feature creation."""
        df = fe.create_all_features(sample_series, sample_series.index)
        
        assert "lag_1" in df.columns
        assert "rolling_mean_7" in df.columns
        assert "day_of_week" in df.columns
        assert "trend" in df.columns
        assert len(df) < len(sample_series)  # Some rows dropped due to NaN


class TestSalaryCycle:
    """Test salary cycle features."""

    def test_mark_salary_days(self):
        """Test salary day marking."""
        from features.salary_cycle import SalaryCycleAnalyzer
        
        analyzer = SalaryCycleAnalyzer()
        dates = pd.date_range("2023-01-01", periods=31)
        
        salary_days = analyzer.mark_salary_days(dates)
        
        # Check known salary dates
        assert salary_days[dates[24]]  # 25th
        assert salary_days[dates[27]]  # 28th
        assert not salary_days[dates[23]]  # 24th


class TestEventCalendar:
    """Test event calendar features."""

    def test_mark_holidays(self):
        """Test holiday marking."""
        from features.event_calendar import EventCalendar
        
        calendar = EventCalendar()
        dates = pd.date_range("2023-01-01", periods=365)
        
        holidays = calendar.mark_holidays(dates)
        
        assert holidays.sum() > 0  # Should find some holidays
        assert isinstance(holidays, pd.Series)

    def test_mark_special_events(self):
        """Test special event marking."""
        from features.event_calendar import EventCalendar
        
        calendar = EventCalendar()
        dates = pd.date_range("2023-01-01", periods=365)
        
        is_event, impacts = calendar.mark_special_events(dates)
        
        assert isinstance(is_event, pd.Series)
        assert isinstance(impacts, dict)
        assert is_event.sum() > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
