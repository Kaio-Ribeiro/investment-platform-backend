import pytest
from fastapi.testclient import TestClient

def test_unauthorized_access(client: TestClient):
    response = client.get("/assets/")
    assert response.status_code == 403

def test_search_yahoo_endpoint_exists(client: TestClient):
    # Test that the endpoint exists (will fail auth, but endpoint is there)
    response = client.get("/assets/search-yahoo/AAPL")
    assert response.status_code == 403  # Unauthorized, but endpoint exists