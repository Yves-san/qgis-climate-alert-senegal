"""LSTM model for temperature/precipitation time-series forecasting."""
from __future__ import annotations
import numpy as np

try:
    import tensorflow as tf
    HAS_TF = True
except ImportError:
    HAS_TF = False


def build_lstm(seq_len: int = 30, n_features: int = 3, horizon: int = 7):
    """Build a 3-layer stacked LSTM. Returns Keras model or None if TF absent."""
    if not HAS_TF:
        return None
    model = tf.keras.Sequential([
        tf.keras.layers.LSTM(64, return_sequences=True, input_shape=(seq_len, n_features)),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.LSTM(64, return_sequences=True),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.LSTM(32),
        tf.keras.layers.Dense(horizon),
    ])
    model.compile(optimizer="adam", loss="huber", metrics=["mae"])
    return model


def simple_forecast(series: np.ndarray, horizon: int = 7) -> np.ndarray:
    """Fallback linear extrapolation when TF is unavailable."""
    x = np.arange(len(series))
    m, c = np.polyfit(x, series, 1)
    return np.array([m * (len(series) + i) + c for i in range(horizon)])
