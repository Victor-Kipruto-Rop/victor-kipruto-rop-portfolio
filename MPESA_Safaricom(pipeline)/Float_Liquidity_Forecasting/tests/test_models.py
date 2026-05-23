"""Tests for forecasting models."""
import pytest
import pandas as pd
import numpy as np

from models.prophet_model import ProphetForecaster
from models.lstm_model import LSTMForecaster
from models.evaluate import ModelEvaluator


class TestProphetForecaster:
    """Test Prophet forecasting model."""

    @pytest.fixture
    def forecaster(self):
        """Create Prophet forecaster."""
        return ProphetForecaster()

    @pytest.fixture
    def sample_series(self):
        """Create sample time series."""
        dates = pd.date_range("2022-01-01", periods=365)
        data = np.sin(np.arange(365) * 2 * np.pi / 365) * 100 + 100 + np.random.randn(365) * 5
        return pd.Series(data, index=dates)

    def test_prepare_data(self, forecaster, sample_series):
        """Test data preparation."""
        df = forecaster.prepare_data(sample_series)
        
        assert "ds" in df.columns
        assert "y" in df.columns
        assert len(df) == len(sample_series)

    def test_train(self, forecaster, sample_series):
        """Test model training."""
        forecaster.train(sample_series)
        
        assert forecaster.model is not None
        assert forecaster.training_data is not None

    def test_forecast(self, forecaster, sample_series):
        """Test forecast generation."""
        forecaster.train(sample_series)
        forecast = forecaster.forecast(periods=7)
        
        assert len(forecast) == 7
        assert "yhat" in forecast.columns
        assert "yhat_lower" in forecast.columns
        assert "yhat_upper" in forecast.columns

    def test_evaluate(self, forecaster, sample_series):
        """Test model evaluation."""
        train_series = sample_series[:300]
        test_series = sample_series[300:]
        
        forecaster.train(train_series)
        metrics = forecaster.evaluate(test_series)
        
        assert "MAE" in metrics
        assert "RMSE" in metrics
        assert "MAPE" in metrics
        assert metrics["MAE"] > 0


class TestLSTMForecaster:
    """Test LSTM forecasting model."""

    @pytest.fixture
    def forecaster(self):
        """Create LSTM forecaster."""
        return LSTMForecaster(epochs=2, batch_size=16)  # Short training for tests

    @pytest.fixture
    def sample_series(self):
        """Create sample time series."""
        dates = pd.date_range("2022-01-01", periods=365)
        data = np.sin(np.arange(365) * 2 * np.pi / 365) * 100 + 100 + np.random.randn(365) * 5
        return pd.Series(data, index=dates)

    def test_prepare_data(self, forecaster, sample_series):
        """Test data preparation."""
        X, y = forecaster.prepare_data(sample_series)
        
        assert X.shape[0] > 0
        assert y.shape[0] > 0
        assert X.shape[0] == y.shape[0]

    def test_train(self, forecaster, sample_series):
        """Test model training."""
        forecaster.train(sample_series, verbose=0)
        
        assert forecaster.model is not None

    def test_forecast(self, forecaster, sample_series):
        """Test forecast generation."""
        forecaster.train(sample_series, verbose=0)
        forecast = forecaster.forecast(sample_series, periods=7)
        
        assert len(forecast) == 7
        assert all(np.isfinite(forecast))

    def test_evaluate(self, forecaster, sample_series):
        """Test model evaluation."""
        train_series = sample_series[:300]
        test_series = sample_series[300:]
        
        forecaster.train(train_series, verbose=0)
        metrics = forecaster.evaluate(test_series)
        
        assert "MAE" in metrics
        assert "RMSE" in metrics
        assert "MAPE" in metrics


class TestModelEvaluator:
    """Test model evaluation utilities."""

    @pytest.fixture
    def predictions(self):
        """Create sample predictions."""
        y_true = np.array([100, 102, 105, 103, 104])
        y_pred = np.array([99, 103, 104, 105, 102])
        return y_true, y_pred

    def test_calculate_mae(self, predictions):
        """Test MAE calculation."""
        y_true, y_pred = predictions
        mae = ModelEvaluator.calculate_mae(y_true, y_pred)
        
        assert mae > 0
        assert isinstance(mae, (float, np.floating))

    def test_calculate_rmse(self, predictions):
        """Test RMSE calculation."""
        y_true, y_pred = predictions
        rmse = ModelEvaluator.calculate_rmse(y_true, y_pred)
        
        assert rmse > 0
        assert isinstance(rmse, (float, np.floating))

    def test_calculate_mape(self, predictions):
        """Test MAPE calculation."""
        y_true, y_pred = predictions
        mape = ModelEvaluator.calculate_mape(y_true, y_pred)
        
        assert mape > 0
        assert isinstance(mape, (float, np.floating))

    def test_get_all_metrics(self, predictions):
        """Test all metrics calculation."""
        y_true, y_pred = predictions
        metrics = ModelEvaluator.get_all_metrics(y_true, y_pred)
        
        assert "MAE" in metrics
        assert "RMSE" in metrics
        assert "MAPE" in metrics
        assert "DirectionalAccuracy" in metrics

    def test_calculate_residuals(self, predictions):
        """Test residual analysis."""
        y_true, y_pred = predictions
        residuals = ModelEvaluator.calculate_residuals(y_true, y_pred)
        
        assert "mean" in residuals
        assert "std" in residuals
        assert "min" in residuals
        assert "max" in residuals


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
