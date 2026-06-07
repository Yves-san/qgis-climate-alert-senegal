"""Unit tests: database schema and session."""
import pytest
from data.database_schema import CommuneClimateData, CommuneMetadata


def test_tables_created(db):
    from sqlalchemy import inspect
    insp = inspect(db.engine)
    tables = insp.get_table_names()
    assert "commune_climate_data" in tables
    assert "commune_metadata" in tables


def test_insert_commune_metadata(session):
    meta = CommuneMetadata(
        commune_id="TST001", commune_name="TestCommune",
        region="TestRegion", latitude=14.7, longitude=-16.9,
    )
    session.add(meta)
    session.commit()
    fetched = session.query(CommuneMetadata).filter_by(commune_id="TST001").first()
    assert fetched.commune_name == "TestCommune"
    assert fetched.region == "TestRegion"


def test_insert_daily_record(session):
    from datetime import datetime
    rec = CommuneClimateData(
        commune_id="TST001", commune_name="TestCommune",
        latitude=14.7, longitude=-16.9,
        date_daily=datetime(2035, 7, 15),
        temp_daily=29.5, precip_daily=8.2, humidity_daily=72.0,
        resolution="daily", scenario="SSP2-4.5",
    )
    session.add(rec)
    session.commit()
    r = session.query(CommuneClimateData).filter_by(commune_id="TST001").first()
    assert r is not None
    assert abs(r.temp_daily - 29.5) < 0.01
