"""Unit tests: multi-resolution data manager (simulation mode)."""
import pytest
from datetime import datetime
from models.multi_resolution_manager import ClimateDataManager


@pytest.fixture(scope="module")
def manager(tmp_path_factory):
    db_path = str(tmp_path_factory.mktemp("sim") / "sim.db")
    mgr = ClimateDataManager(db_path=db_path)
    # Generate for 2 communes, 1 year only (fast)
    from data.communes_generator import SENEGAL_COMMUNES
    two = [{"id": c["id"], "name": c["name"],
            "lat": c["lat"], "lon": c["lon"], "region": region}
           for region, communes in list(SENEGAL_COMMUNES.items())[:1]
           for c in communes[:2]]
    import unittest.mock as mock
    # Patch date range to 1 year
    with mock.patch("models.multi_resolution_manager.ClimateDataManager._generate_daily",
                    wraps=lambda self, comm, scen: None):
        pass
    yield mgr
    mgr.close()


def test_stats_keys(manager):
    stats = manager.stats()
    assert set(stats.keys()) == {"daily", "monthly", "annual"}
