"""Unit tests: climate indicators."""
import numpy as np
import pytest
from models.climate_indicators import ClimateIndicators


def test_spi_output_shape():
    p = np.random.exponential(5, 365)
    spi = ClimateIndicators.spi(p)
    assert spi.shape == p.shape


def test_drought_index_range():
    t = np.full(12, 30.0)
    p = np.zeros(12)
    h = np.full(12, 40.0)
    di = ClimateIndicators.drought_index(t, p, h)
    assert np.all(di >= 0) and np.all(di <= 1)


def test_classify_critical():
    level, _ = ClimateIndicators.classify(0.9, 0.9, 0)
    assert level == "CRITICAL"


def test_classify_low():
    level, _ = ClimateIndicators.classify(0.1, 0.1, 20)
    assert level == "LOW"


def test_recommendations_not_empty():
    recs = ClimateIndicators.agricultural_recommendations("HIGH", 34, 1, 0.7)
    assert len(recs) >= 1
