"""
Senegal Climate Alert System — FastAPI REST API
Endpoints: /climate, /predictions, /alerts, /export, /analysis
"""
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Optional
from data.database_schema import DatabaseManager
from models.climate_query_engine import QueryEngine
from models.climate_indicators import ClimateIndicators
import numpy as np

app = FastAPI(
    title="Senegal Climate Alert API",
    description="Climate projection data for 557 Senegal communes (2025-2055)",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_db = None
_qe = None

def get_qe() -> QueryEngine:
    global _db, _qe
    if _qe is None:
        _db = DatabaseManager()
        _qe = QueryEngine(_db)
    return _qe


@app.get("/")
def root():
    return {"message": "Senegal Climate Alert API v2.0", "docs": "/docs"}


@app.get("/api/communes")
def list_communes(resolution: str = "monthly", scenario: str = "SSP2-4.5"):
    return {"communes": get_qe().list_communes(resolution, scenario)}


@app.get("/api/climate/{resolution}")
def climate_data(
    resolution: str,
    commune: str = Query(..., description="Commune name"),
    start: str  = Query("2025-01-01"),
    end:   str  = Query("2055-12-31"),
    scenario: str = Query("SSP2-4.5"),
):
    try:
        df = get_qe().get_data(
            commune,
            datetime.fromisoformat(start),
            datetime.fromisoformat(end),
            resolution, scenario,
        )
    except ValueError as e:
        raise HTTPException(400, str(e))
    if df.empty:
        raise HTTPException(404, f"No data for {commune}")
    return df.fillna(0).to_dict(orient="records")


@app.get("/api/statistics/{commune}")
def statistics(commune: str, scenario: str = "SSP2-4.5"):
    qe  = get_qe()
    avg = qe.get_extremes(commune, datetime(2025,1,1), datetime(2055,12,31),
                          "annual", scenario)
    trnd = qe.get_trend(commune, datetime(2025,1,1), datetime(2055,12,31),
                        "annual", scenario)
    return {"commune": commune, "extremes": avg, "trends": trnd}


@app.get("/api/risk/{commune}")
def risk(commune: str, year: int = 2035, scenario: str = "SSP2-4.5"):
    qe = get_qe()
    df = qe.get_data(commune, datetime(year,1,1), datetime(year,12,31),
                     "monthly", scenario)
    if df.empty:
        raise HTTPException(404, "No data")
    di = ClimateIndicators.drought_index(
        df["temperature"].values, df["precipitation"].values, df["humidity"].values
    ).mean()
    hs = ClimateIndicators.heat_stress(
        df["temperature"].values, df["humidity"].values
    ).mean()
    level, desc = ClimateIndicators.classify(float(di), float(hs),
                                              float(df["precipitation"].mean()))
    recs = ClimateIndicators.agricultural_recommendations(
        level, float(df["temperature"].mean()),
        float(df["precipitation"].mean()), float(di)
    )
    return {
        "commune": commune, "year": year, "scenario": scenario,
        "risk_level": level, "description": desc,
        "drought_index": round(float(di), 3),
        "heat_stress": round(float(hs), 3),
        "recommendations": recs,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
