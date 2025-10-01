import pytest
from fastapi.testclient import TestClient

def test_unauthorized_access(client: TestClient):
    response = client.get("/clients/")
    assert response.status_code == 403  # FastAPI Security returns 403 for missing auth

def test_api_is_running(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Investment API is running!"}