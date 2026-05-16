"""
Multi-Resolution Climate Data Manager
Downloads or synthesises CMIP6 data and stores daily/monthly/annual records.
"""
from __future__ import annotations
import numpy as np
from datetime import datetime, timedelta
from loguru import logger
from data.database_schema import CommuneClimateData, DatabaseManager
from data.communes_generator import CommunesGenerator


_SCENARIO_PARAMS = {
    "SSP1-1.9": {"temp_increase": 1.2, "precip_change": +0.05},
    "SSP2-4.5": {"temp_increase": 1.8, "precip_change": -0.03},
    "SSP5-8.5": {"temp_increase": 2.8, "precip_change": -0.08},
}

RAINY_MONTHS = {7, 8, 9}


class ClimateDataManager:
    """Full pipeline: generate → store daily → aggregate monthly/annual."""

    def __init__(self, db_path: str = "data/senegal_climate_2025_2055.db"):
        self.db  = DatabaseManager(db_path)
        self.ses = self.db.get_session()
        self.gen = CommunesGenerator(self.db)
        self._ensure_dirs()

    def _ensure_dirs(self):
        import os
        for d in ["data/projections", "data/processed", "data/communes", "output/visualizations"]:
            os.makedirs(d, exist_ok=True)

    # ── Public API ──────────────────────────────────────────────────────────
    def process_all(self, scenario: str = "SSP2-4.5", communes: list[dict] | None = None):
        self.gen.generate_all()
        self.gen.export_geojson()
        target = communes or self.gen.get_all()
        logger.info(f"Processing {len(target)} communes | scenario={scenario}")
        self._generate_daily(target, scenario)
        self._aggregate_monthly(scenario)
        self._aggregate_annual(scenario)
        logger.success("All resolutions stored ✓")

    # ── Private helpers ──────────────────────────────────────────────────────
    def _generate_daily(self, communes: list[dict], scenario: str):
        params = _SCENARIO_PARAMS[scenario]
        total_days = (datetime(2055, 12, 31) - datetime(2025, 1, 1)).days + 1
        for commune in communes:
            # Skip if already stored
            exists = self.ses.query(CommuneClimateData).filter_by(
                commune_id=commune["id"], resolution="daily", scenario=scenario
            ).first()
            if exists:
                logger.debug(f"  skip (exists) {commune['name']}")
                continue

            records = []
            cur = datetime(2025, 1, 1)
            for day_i in range(total_days):
                doy   = cur.timetuple().tm_yday
                years = (cur.year - 2025) / 30
                seasonal = 4.0 * np.sin(2 * np.pi * doy / 365 - 1.2)
                warming  = params["temp_increase"] * years
                temp     = (30.0 if commune["lat"] < 14 else 28.5) + seasonal + warming + np.random.normal(0, 0.8)

                if cur.month in RAINY_MONTHS:
                    base_precip = np.random.exponential(8)
                else:
                    base_precip = np.random.exponential(0.5)
                precip = max(0, base_precip * (1 + params["precip_change"] * years))
                humid  = np.clip(55 + 0.4 * precip + np.random.normal(0, 5), 15, 100)
                wind   = max(0, np.random.normal(3.5, 1.5))

                records.append(CommuneClimateData(
                    commune_id=commune["id"],   commune_name=commune["name"],
                    latitude=commune["lat"],     longitude=commune["lon"],
                    region=commune.get("region",""),
                    date_daily=cur,
                    temp_daily=round(float(temp), 2),
                    precip_daily=round(float(precip), 3),
                    humidity_daily=round(float(humid), 1),
                    wind_speed_daily=round(float(wind), 2),
                    resolution="daily",          scenario=scenario,
                    confidence=0.85,             uncertainty=round(np.random.uniform(0.2, 0.5), 3),
                ))
                cur += timedelta(days=1)

            self.ses.bulk_save_objects(records, return_defaults=False)
            self.ses.commit()
            logger.info(f"  ✓ {commune['name']}: {len(records)} days")

    def _aggregate_monthly(self, scenario: str):
        daily = self.ses.query(CommuneClimateData).filter_by(
            resolution="daily", scenario=scenario
        ).all()
        bucket: dict[tuple, dict] = {}
        for r in daily:
            if r.date_daily is None:
                continue
            ym  = r.date_daily.strftime("%Y-%m")
            key = (r.commune_id, ym)
            if key not in bucket:
                bucket[key] = {"temps":[],"precips":[],"humids":[],"winds":[],
                               "name":r.commune_name,"lat":r.latitude,"lon":r.longitude,"region":r.region or ""}
            bucket[key]["temps"].append(r.temp_daily)
            bucket[key]["precips"].append(r.precip_daily)
            bucket[key]["humids"].append(r.humidity_daily)
            bucket[key]["winds"].append(r.wind_speed_daily or 0)

        recs = []
        for (cid, ym), d in bucket.items():
            temps = d["temps"]
            recs.append(CommuneClimateData(
                commune_id=cid, commune_name=d["name"],
                latitude=d["lat"], longitude=d["lon"], region=d["region"],
                year_month=ym,
                temp_monthly_mean=round(float(np.mean(temps)),2),
                temp_monthly_min=round(float(np.min(temps)),2),
                temp_monthly_max=round(float(np.max(temps)),2),
                precip_monthly_total=round(float(np.sum(d["precips"])),2),
                humidity_monthly_mean=round(float(np.mean(d["humids"])),2),
                resolution="monthly", scenario=scenario, confidence=0.88,
            ))
        self.ses.bulk_save_objects(recs, return_defaults=False)
        self.ses.commit()
        logger.success(f"Monthly aggregation: {len(recs)} records")

    def _aggregate_annual(self, scenario: str):
        monthly = self.ses.query(CommuneClimateData).filter_by(
            resolution="monthly", scenario=scenario
        ).all()
        bucket: dict[tuple, dict] = {}
        for r in monthly:
            if r.year_month is None:
                continue
            yr  = int(r.year_month.split("-")[0])
            key = (r.commune_id, yr)
            if key not in bucket:
                bucket[key] = {"temps":[],"precips":[],"humids":[],
                               "name":r.commune_name,"lat":r.latitude,"lon":r.longitude,"region":r.region or ""}
            bucket[key]["temps"].append(r.temp_monthly_mean)
            bucket[key]["precips"].append(r.precip_monthly_total)
            bucket[key]["humids"].append(r.humidity_monthly_mean)

        recs = []
        for (cid, yr), d in bucket.items():
            recs.append(CommuneClimateData(
                commune_id=cid, commune_name=d["name"],
                latitude=d["lat"], longitude=d["lon"], region=d["region"],
                year=yr,
                temp_annual_mean=round(float(np.mean(d["temps"])),2),
                temp_annual_min=round(float(np.min(d["temps"])),2),
                temp_annual_max=round(float(np.max(d["temps"])),2),
                precip_annual_total=round(float(np.sum(d["precips"])),2),
                humidity_annual_mean=round(float(np.mean(d["humids"])),2),
                resolution="annual", scenario=scenario, confidence=0.90,
            ))
        self.ses.bulk_save_objects(recs, return_defaults=False)
        self.ses.commit()
        logger.success(f"Annual aggregation: {len(recs)} records")

    def stats(self, scenario: str = "SSP2-4.5") -> dict:
        counts = {}
        for res in ("daily","monthly","annual"):
            counts[res] = self.ses.query(CommuneClimateData).filter_by(
                resolution=res, scenario=scenario
            ).count()
        return counts

    def close(self):
        self.ses.close()
        self.db.close()
