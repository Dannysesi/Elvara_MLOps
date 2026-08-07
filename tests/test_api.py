from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["service"] == "elvara-sepsis-cdss"
    assert "model_loaded" in json_data

def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "elvara_sepsis" in response.text
