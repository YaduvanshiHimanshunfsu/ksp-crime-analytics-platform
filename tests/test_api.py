import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "data": "synthetic"}

def test_overview():
    response = client.get("/api/v1/overview")
    assert response.status_code == 200
    data = response.json()
    assert "total_cases" in data
    assert "synthetic_notice" in data

def test_risk_forecast():
    response = client.get("/api/v1/risk-forecast")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        forecast = data[0]
        assert "area" in forecast
        assert "risk_score" in forecast
        assert "drivers" in forecast
        assert isinstance(forecast["drivers"], list)
        if len(forecast["drivers"]) > 0:
            driver = forecast["drivers"][0]
            assert "readable_name" in driver
            assert "direction" in driver

def test_district_benchmark():
    response = client.get("/api/v1/district-benchmark")
    assert response.status_code == 200
    res = response.json()
    assert "districts" in res
    data = res["districts"]
    assert isinstance(data, list)
    if len(data) > 0:
        assert "drishti_district" in data[0]
        assert "ipc_bns_crimes" in data[0]

def test_district_trends():
    response = client.get("/api/v1/district-trends")
    assert response.status_code == 200
    res = response.json()
    assert "data" in res
    data = res["data"]
    assert isinstance(data, list)

def test_alert_feedback():
    payload = {"useful": True, "reason": "Accurate prediction based on recent patterns."}
    response = client.post("/api/v1/alerts/h3-demo-999/feedback", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["stored"] is True
    assert data["alert_id"] == "h3-demo-999"
