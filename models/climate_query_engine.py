"""
Flexible query engine for daily / monthly / annual climate data.
Provides trend analysis, export to CSV and extreme-value detection.
"""
from __future__ import annotations
from datetime import datetime
from typing import Any
import numpy as np
import pandas as pd
from loguru import logger
from data.database_schema import CommuneClimateData, DatabaseManager


class QueryEngine:
    """High-level interface for querying the climate DB."""

    def __init__(self, db: DatabaseManager):
        self.db  = db
        self.ses = db.get_session()

    # ── Main query ──────────────────────────────────────────────────────────
    def get_data(
        self,
        commune_name: str,
        start: datetime,
        end: datetime,
        resolution: str = "monthly",
        scenario: str = "SSP2-4.5",
    ) -> pd.DataFrame:
        if resolution not in {"daily", "monthly", "annual"}:
            raise ValueError(f"Unknown resolution: {resolution}")

        q = self.ses.query(CommuneClimateData).filter_by(
            commune_name=commune_name,
            resolution=resolution,
            scenario=scenario,
        )
        if resolution == "daily":
            q = q.filter(CommuneClimateData.date_daily.between(start, end))
        elif resolution == "monthly":
            q = q.filter(
                CommuneClimateData.year_month.between(
                    start.strftime("%Y-%m"), end.strftime("%Y-%m")
                )
            )
        else:
            q = q.filter(CommuneClimateData.year.between(start.year, end.year))

        rows = q.order_by(
            CommuneClimateData.date_daily or
            CommuneClimateData.year_month or
            CommuneClimateData.year
        ).all()

        if not rows:
            logger.warning(f"No data for {commune_name} ({resolution}, {scenario})")
            return pd.DataFrame()

        return self._to_df(rows, resolution)

    def _to_df(self, rows: list, resolution: str) -> pd.DataFrame:
        data: list[dict[str, Any]] = []
        for r in rows:
            if resolution == "daily":
                row = {"date": r.date_daily,
                       "temperature": r.temp_daily, "temperature_min": r.temp_daily,
                       "temperature_max": r.temp_daily,
                       "precipitation": r.precip_daily or 0,
                       "humidity": r.humidity_daily, "wind_speed": r.wind_speed_daily or 0}
            elif resolution == "monthly":
                row = {"date": r.year_month,
                       "temperature": r.temp_monthly_mean,
                       "temperature_min": r.temp_monthly_min,
                       "temperature_max": r.temp_monthly_max,
                       "precipitation": r.precip_monthly_total or 0,
                       "humidity": r.humidity_monthly_mean, "wind_speed": 0}
            else:
                row = {"date": str(r.year),
                       "temperature": r.temp_annual_mean,
                       "temperature_min": r.temp_annual_min,
                       "temperature_max": r.temp_annual_max,
                       "precipitation": r.precip_annual_total or 0,
                       "humidity": r.humidity_annual_mean, "wind_speed": 0}
            row.update({"drought_index": r.drought_index, "risk_level": r.risk_level or "UNKNOWN",
                        "confidence": r.confidence or 0.5})
            data.append(row)
        return pd.DataFrame(data)

    # ── Analytics ──────────────────────────────────────────────────────────
    def get_trend(self, commune_name: str, start: datetime, end: datetime,
                  resolution: str = "annual", scenario: str = "SSP2-4.5") -> dict:
        df = self.get_data(commune_name, start, end, resolution, scenario)
        if df.empty or len(df) < 2:
            return {}
        result = {}
        for col in ("temperature", "precipitation", "humidity"):
            y = df[col].values.astype(float)
            x = np.arange(len(y))
            m, c = np.polyfit(x, y, 1)
            yp = m * x + c
            ss_res = np.sum((y - yp) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
            result[col] = {
                "slope": round(float(m), 4),
                "r_squared": round(float(r2), 4),
                "forecast_next": round(float(m * len(y) + c), 2),
                "direction": "increasing" if m > 0 else "decreasing",
            }
        return result

    def get_extremes(self, commune_name: str, start: datetime, end: datetime,
                     resolution: str = "monthly", scenario: str = "SSP2-4.5") -> dict:
        df = self.get_data(commune_name, start, end, resolution, scenario)
        if df.empty:
            return {}
        return {
            "temp_max": round(float(df["temperature_max"].max()), 2),
            "temp_min": round(float(df["temperature_min"].min()), 2),
            "precip_max": round(float(df["precipitation"].max()), 2),
            "precip_total": round(float(df["precipitation"].sum()), 2),
        }

    def list_communes(self, resolution: str = "monthly",
                      scenario: str = "SSP2-4.5") -> list[str]:
        rows = (
            self.ses.query(CommuneClimateData.commune_name)
            .filter_by(resolution=resolution, scenario=scenario)
            .distinct().all()
        )
        return sorted(r[0] for r in rows)

    def export_csv(self, commune: str, start: datetime, end: datetime,
                   resolution: str = "monthly", scenario: str = "SSP2-4.5",
                   path: str = "output/export.csv") -> str:
        import os; os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        df = self.get_data(commune, start, end, resolution, scenario)
        df.to_csv(path, index=False)
        logger.success(f"Exported {len(df)} rows → {path}")
        return path

    def close(self):
        self.ses.close()
