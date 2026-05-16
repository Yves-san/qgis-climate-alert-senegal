"""
SQLAlchemy models — multi-resolution climate data store.
Handles daily / monthly / annual aggregations + risk indicators.
"""
from __future__ import annotations
import os
from datetime import datetime
from sqlalchemy import (
    create_engine, Column, Integer, Float, String,
    DateTime, Index, event
)
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from loguru import logger


class Base(DeclarativeBase):
    pass


class CommuneClimateData(Base):
    """Main table: one row per (commune, date, resolution, scenario)."""
    __tablename__ = "commune_climate_data"
    __table_args__ = (
        Index("ix_ccd_commune_res_scenario", "commune_id", "resolution", "scenario"),
        Index("ix_ccd_date",       "date_daily"),
        Index("ix_ccd_year_month", "year_month"),
        Index("ix_ccd_year",       "year"),
    )

    id           = Column(Integer, primary_key=True, autoincrement=True)
    commune_id   = Column(String(50),  nullable=False)
    commune_name = Column(String(100), nullable=False)
    latitude     = Column(Float,       nullable=False)
    longitude    = Column(Float,       nullable=False)
    region       = Column(String(50))

    # Daily
    date_daily        = Column(DateTime)
    temp_daily        = Column(Float)
    precip_daily      = Column(Float)
    humidity_daily    = Column(Float)
    wind_speed_daily  = Column(Float)

    # Monthly
    year_month            = Column(String(7))
    temp_monthly_mean     = Column(Float)
    temp_monthly_min      = Column(Float)
    temp_monthly_max      = Column(Float)
    precip_monthly_total  = Column(Float)
    humidity_monthly_mean = Column(Float)

    # Annual
    year                 = Column(Integer)
    temp_annual_mean     = Column(Float)
    temp_annual_min      = Column(Float)
    temp_annual_max      = Column(Float)
    precip_annual_total  = Column(Float)
    humidity_annual_mean = Column(Float)

    # Risk indicators
    drought_index    = Column(Float)
    spi_index        = Column(Float)
    heat_stress      = Column(Float)
    ndvi_estimate    = Column(Float)
    risk_level       = Column(String(10))

    # Metadata
    resolution  = Column(String(10), nullable=False)
    confidence  = Column(Float,  default=0.85)
    uncertainty = Column(Float)
    scenario    = Column(String(20))
    model_name  = Column(String(50))
    created_at  = Column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        ts = self.date_daily or self.year_month or self.year
        return f"<ClimateData {self.commune_name} {ts}>"


class CommuneMetadata(Base):
    """Spatial + socio-economic metadata for each commune."""
    __tablename__ = "commune_metadata"

    id           = Column(Integer,    primary_key=True)
    commune_id   = Column(String(50), unique=True, nullable=False)
    commune_name = Column(String(100), nullable=False)
    region       = Column(String(50))
    latitude     = Column(Float,       nullable=False)
    longitude    = Column(Float,       nullable=False)
    population   = Column(Integer)
    area_km2     = Column(Float)
    main_crops   = Column(String(200))
    geojson      = Column(String)

    def __repr__(self) -> str:
        return f"<Commune {self.commune_name} ({self.region})>"


class DatabaseManager:
    """Connection pool + table creation helper."""

    def __init__(self, db_path: str = "data/senegal_climate_2025_2055.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        self.engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},
            pool_pre_ping=True,
        )
        # Enable WAL for better concurrency
        @event.listens_for(self.engine, "connect")
        def set_wal(dbapi_conn, _):
            dbapi_conn.execute("PRAGMA journal_mode=WAL")
            dbapi_conn.execute("PRAGMA cache_size=-64000")  # 64 MB cache

        Base.metadata.create_all(self.engine)
        self._Session = sessionmaker(bind=self.engine)
        logger.success(f"Database ready: {db_path}")

    def get_session(self) -> Session:
        return self._Session()

    def close(self) -> None:
        self.engine.dispose()


if __name__ == "__main__":
    db = DatabaseManager()
    print("✅ Schema created successfully")
    db.close()
