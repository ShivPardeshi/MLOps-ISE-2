"""
Unit and Integration Test Suite for student-app
Executed during Jenkins CI 'Test & Quality Gate' Stage
"""

import pytest
from app import app


@pytest.fixture
def client():
    """Create test client for Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_home_page(client):
    """Verify that home page loads successfully (HTTP 200)."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Student Performance Predictor" in response.data
    assert b"Forecast Performance" in response.data


def test_health_endpoint(client):
    """Verify Docker / Kubernetes health probe endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["status"] == "healthy"
    assert json_data["service"] == "student-app"
    assert "model_loaded" in json_data


def test_predict_api_json(client):
    """Verify JSON REST API prediction with valid attributes."""
    payload = {
        "studytime": 4,
        "failures": 0,
        "absences": 2,
        "Medu": 4,
        "Fedu": 4,
        "higher": "yes",
        "internet": "yes",
        "health": 5
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["status"] == "success"
    assert "predicted_grade" in json_data
    assert 0.0 <= json_data["predicted_grade"] <= 20.0
    assert json_data["percentage"] == round((json_data["predicted_grade"] / 20.0) * 100, 1)
    assert "tier" in json_data


def test_predict_form_post(client):
    """Verify HTML form submission and server-rendered prediction."""
    form_data = {
        "studytime": "3",
        "failures": "0",
        "absences": "4",
        "Medu": "3",
        "Fedu": "3",
        "higher": "yes",
        "internet": "yes",
        "health": "4"
    }
    response = client.post("/predict", data=form_data)
    assert response.status_code == 200
    assert b"Prediction &amp; Pipeline Status" in response.data or b"Prediction & Pipeline Status" in response.data
    assert b"/ 20" in response.data


def test_studytime_impact_logic(client):
    """Verify that diligent study profile scores higher than high failure profile."""
    high_perf_payload = {
        "studytime": 4,
        "failures": 0,
        "absences": 0,
        "higher": "yes"
    }
    low_perf_payload = {
        "studytime": 1,
        "failures": 3,
        "absences": 25,
        "higher": "no"
    }

    res_high = client.post("/predict", json=high_perf_payload).get_json()
    res_low = client.post("/predict", json=low_perf_payload).get_json()

    assert res_high["predicted_grade"] > res_low["predicted_grade"], (
        f"Expected higher grade for diligent profile ({res_high['predicted_grade']}) "
        f"vs at-risk profile ({res_low['predicted_grade']})"
    )
