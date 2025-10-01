import pytest
from fastapi.testclient import TestClient

def test_unauthorized_access(client: TestClient):
    response = client.get("/allocations/")
    assert response.status_code == 403

def test_total_allocation_endpoint_exists(client: TestClient):
    response = client.get("/allocations/total-allocation")
    assert response.status_code == 403