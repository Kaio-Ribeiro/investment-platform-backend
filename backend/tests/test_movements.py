import pytest
from fastapi.testclient import TestClient

def test_unauthorized_access(client: TestClient):
    response = client.get("/movements/")
    assert response.status_code == 403

def test_captation_total_endpoint_exists(client: TestClient):
    response = client.get("/movements/captation-total")
    assert response.status_code == 403