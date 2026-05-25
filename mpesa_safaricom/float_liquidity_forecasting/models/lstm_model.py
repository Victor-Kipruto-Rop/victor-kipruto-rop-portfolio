"""LSTM neural network forecasting model."""
from typing import Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow import keras
from tensorflow.keras import layers, models
from tensorflow.keras.callbacks import (
    EarlyStopping,
    ModelCheckpoint,
    ReduceLROnPlateau,
)

from config import settings
from logger import logger


class LSTMForecaster:
    """LSTM-based deep learning forecaster."""

    def __init__(
        self,
        units: int = 64,
        dropout: float = 0.2,
        batch_size: int = 32,
        epochs: int = 50,
        validation_split: float = 0.1,
        lookback: int = 30,
    ):
        """
        Initialize LSTM forecaster.

        Args:
            units: Number of LSTM units
            dropout: Dropout rate
            batch_size: Batch size
            epochs: Number of epochs
            validation_split: Validation split ratio
            lookback: Number of previous timesteps to use
        """
        self.units = units
        self.dropout = dropout
        self.batch_size = batch_size
        self.epochs = epochs
        self.validation_split = validation_split
        self.lookback = lookback
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.training_data = None

    def create_sequences(
        self, data: np.ndarray, lookback: int
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create sequences for LSTM training.

        Args:
            data: Input data
            lookback: Number of previous timesteps

        Returns:
            Tuple of (X, y) sequences
        """
        X, y = [], []

        for i in range(len(data) - lookback):
            X.append(data[i : i + lookback])
            y.append(data[i + lookback])

        return np.array(X), np.array(y)

    def prepare_data(self, series: pd.Series) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare data for LSTM.

        Args:
            series: Time series data

        Returns:
            Tuple of (X, y) for training
        """
        # Reshape for scaler
        data = series.values.reshape(-1, 1)
        scaled_data = self.scaler.fit_transform(data)

        # Create sequences
        X, y = self.create_sequences(scaled_data, self.lookback)

        logger.info(f"Prepared {len(X)} sequences for LSTM training")
        return X, y

    def build_model(self, input_shape: Tuple) -> models.Sequential:
        """
        Build LSTM model.

        Args:
            input_shape: Input shape

        Returns:
            Compiled Keras model
        """
        model = models.Sequential(
            [
                layers.LSTM(
                    self.units,
                    activation="relu",
                    input_shape=input_shape,
                    return_sequences=True,
                ),
                layers.Dropout(self.dropout),
                layers.LSTM(
                    self.units // 2,
                    activation="relu",
                    return_sequences=False,
                ),
                layers.Dropout(self.dropout),
                layers.Dense(25, activation="relu"),
                layers.Dense(1),
            ]
        )

        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss="mean_squared_error",
            metrics=["mae"],
        )

        logger.info("LSTM model built successfully")
        return model

    def train(
        self,
        series: pd.Series,
        validation_series: Optional[pd.Series] = None,
        verbose: int = 0,
    ):
        """
        Train LSTM model.

        Args:
            series: Historical time series
            validation_series: Optional validation series
            verbose: Verbosity level
        """
        try:
            # Prepare data
            X, y = self.prepare_data(series)

            # Build model
            input_shape = (X.shape[1], 1)
            self.model = self.build_model((input_shape[0], 1))

            # Callbacks
            early_stop = EarlyStopping(
                monitor="val_loss", patience=5, restore_best_weights=True
            )
            reduce_lr = ReduceLROnPlateau(
                monitor="val_loss",
                factor=0.5,
                patience=3,
                min_lr=1e-6,
            )

            # Train model
            self.model.fit(
                X,
                y,
                batch_size=self.batch_size,
                epochs=self.epochs,
                validation_split=self.validation_split,
                callbacks=[early_stop, reduce_lr],
                verbose=verbose,
            )

            logger.info("LSTM model training completed")

        except Exception as e:
            logger.error(f"Model training failed: {e}")
            raise

    def forecast(self, series: pd.Series, periods: int = 7) -> np.ndarray:
        """
        Generate forecast.

        Args:
            series: Recent history for context
            periods: Number of periods to forecast

        Returns:
            Array with forecasted values
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")

        try:
            # Prepare last sequence
            data = series.values.reshape(-1, 1)
            scaled_data = self.scaler.transform(data)

            last_sequence = scaled_data[-self.lookback :]
            predictions = []

            for _ in range(periods):
                # Predict next value
                next_pred = self.model.predict(
                    last_sequence.reshape(1, self.lookback, 1),
                    verbose=0,
                )

                predictions.append(next_pred[0, 0])

                # Update sequence
                last_sequence = np.append(last_sequence[1:], next_pred)

            # Inverse transform
            predictions = np.array(predictions).reshape(-1, 1)
            predictions = self.scaler.inverse_transform(predictions)

            logger.info(f"Generated {periods}-period forecast")
            return predictions.flatten()

        except Exception as e:
            logger.error(f"Forecast generation failed: {e}")
            raise

    def evaluate(
        self, test_series: pd.Series
    ) -> dict:
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
            from sklearn.metrics import mean_absolute_error, mean_squared_error

            # Prepare test data
            X_test, y_test = self.prepare_data(test_series)

            # Make predictions
            y_pred = self.model.predict(X_test, verbose=0)

            # Inverse transform
            y_test_inv = self.scaler.inverse_transform(y_test.reshape(-1, 1))
            y_pred_inv = self.scaler.inverse_transform(y_pred)

            mae = mean_absolute_error(y_test_inv, y_pred_inv)
            rmse = np.sqrt(mean_squared_error(y_test_inv, y_pred_inv))
            mape = (
                np.mean(np.abs((y_test_inv - y_pred_inv) / y_test_inv)) * 100
            )

            metrics = {"MAE": mae, "RMSE": rmse, "MAPE": mape}
            logger.info(f"Evaluation metrics: {metrics}")

            return metrics

        except Exception as e:
            logger.error(f"Model evaluation failed: {e}")
            raise

    def save_model(self, path: str):
        """Save model to disk."""
        if self.model is None:
            raise ValueError("Model not trained.")

        self.model.save(path)
        logger.info(f"Model saved to {path}")

    def load_model(self, path: str):
        """Load model from disk."""
        self.model = keras.models.load_model(path)
        logger.info(f"Model loaded from {path}")
