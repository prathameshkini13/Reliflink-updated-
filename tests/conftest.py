"""Pytest test fixtures and configuration for Disaster Relief Platform."""
import os
import sys
import pytest

# Ensure app/ is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app")))

from app import app as flask_app
from core import DEFAULT_WAREHOUSE


@pytest.fixture
def app():
    flask_app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,  # Disabled for straightforward API testing
        "SECRET_KEY": "test-secret-key-for-unit-testing",
    })
    return flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def csrf_client():
    """Client with CSRF enforcement turned on to test CSRF defense."""
    flask_app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": True,
        "SECRET_KEY": "test-secret-key-enforce-csrf",
    })
    yield flask_app.test_client()
    flask_app.config["WTF_CSRF_ENABLED"] = False


@pytest.fixture
def valid_incident():
    return {
        "zone_id": "Sector-Alpha Delta",
        "disaster_type": "Flash Flood",
        "affected_population": 3500,
        "vulnerability_index": 0.65,
        "infrastructure_damage_pct": 55.0,
        "urgency_window_hours": 14.0,
        "distance_km": 30.0,
    }


@pytest.fixture
def sample_csv_text():
    return (
        "zone_id,disaster_type,affected_population,vulnerability_index,"
        "infrastructure_damage_pct,urgency_window_hours,distance_km\n"
        "Zone-1,Earthquake,5000,0.8,70.0,12.0,25.0\n"
        "Zone-2,Cyclone,2000,0.5,40.0,24.0,50.0\n"
    )
