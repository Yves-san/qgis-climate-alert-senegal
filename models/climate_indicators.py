"""
Climate risk indicators: SPI, drought index, heat stress, NDVI estimate.
"""
from __future__ import annotations
import numpy as np
import pandas as pd


class ClimateIndicators:

    @staticmethod
    def spi(precipitation: np.ndarray, window: int = 30) -> np.ndarray:
        """Standardised Precipitation Index (negative = drought)."""
        series = pd.Series(precipitation)
        rolling = series.rolling(window, center=True, min_periods=1).mean()
        mu, sigma = np.nanmean(rolling), np.nanstd(rolling)
        return np.nan_to_num((rolling.values - mu) / (sigma + 1e-8))

    @staticmethod
    def drought_index(temp: np.ndarray, precip: np.ndarray,
                      humid: np.ndarray) -> np.ndarray:
        """Composite drought index 0-1 (1 = most severe)."""
        t = np.clip((temp - 20) / 40, 0, 1)
        p = 1 - np.clip(precip / 50, 0, 1)
        h = 1 - np.clip(humid / 100, 0, 1)
        return np.clip(0.4 * t + 0.4 * p + 0.2 * h, 0, 1)

    @staticmethod
    def heat_stress(temp: np.ndarray, humid: np.ndarray) -> np.ndarray:
        """Simplified wet-bulb temperature proxy, scaled 0-1."""
        wbt = (temp * np.arctan(0.151977 * np.sqrt(humid + 8.313659))
               + 0.00391838 * humid ** 1.5 * np.arctan(0.023101 * humid))
        return np.clip((wbt - 20) / 20, 0, 1)

    @staticmethod
    def ndvi_estimate(temp: np.ndarray, precip: np.ndarray) -> np.ndarray:
        """Proxy NDVI from temperature + precipitation."""
        tf = 1 - np.abs(temp - 25) / 30
        pf = np.clip(precip / 50, 0, 1)
        return np.clip((0.5 * tf + 0.5 * pf) * 2 - 1, -1, 1)

    @staticmethod
    def classify(drought: float, heat: float, precip: float) -> tuple[str, str]:
        score = 0.4 * drought + 0.3 * heat + 0.3 * (1 if precip < 2 else 0)
        if score > 0.75: return "CRITICAL", "Extrêmement grave — action immédiate"
        if score > 0.50: return "HIGH",     "Grave — surveillance rapprochée"
        if score > 0.25: return "MEDIUM",   "Modéré — alerte préventive"
        return "LOW", "Faible — situation normale"

    @staticmethod
    def agricultural_recommendations(
        risk: str, temp: float, precip: float, drought: float
    ) -> list[str]:
        recs: list[str] = []
        if risk == "CRITICAL":
            recs += ["🚨 URGENCE: irriguer immédiatement", "⚠️ Cultures résistantes recommandées"]
        elif risk == "HIGH":
            recs += ["⚠️ Augmenter la fréquence d'irrigation", "🌱 Réduire la densité de semis"]
        elif risk == "MEDIUM":
            recs += ["💧 Irrigation régulière conseillée", "📊 Surveiller l'évolution"]
        else:
            recs += ["✅ Conditions favorables", "🌾 Continuer le suivi habituel"]
        if temp > 35:
            recs.append("🌞 Chaleur extrême — irrigation goutte-à-goutte recommandée")
        if precip < 2:
            recs.append("💧 Très peu de pluie — irrigation essentielle")
        elif precip > 100:
            recs.append("🌧️ Fortes pluies — drainer les champs si nécessaire")
        return recs
