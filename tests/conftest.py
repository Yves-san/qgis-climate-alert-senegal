"""Pytest configuration and shared fixtures."""
import pytest
from data.database_schema import DatabaseManager

@pytest.fixture(scope="session")
def db(tmp_path_factory):
    p = tmp_path_factory.mktemp("db") / "test.db"
    db = DatabaseManager(str(p))
    yield db
    db.close()

@pytest.fixture
def session(db):
    s = db.get_session()
    yield s
    s.close()
