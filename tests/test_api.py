"""Integration tests: FastAPI endpoints."""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from api.main import app
    return TestClient(app)


def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "Senegal" in r.json()["message"]


def test_communes_endpoint(client):
    r = client.get("/api/communes")
    assert r.status_code == 200
    assert "communes" in r.json()


def test_invalid_resolution(client):
    r = client.get("/api/climate/weekly?commune=Dakar")
    assert r.status_code in (400, 422, 404)
