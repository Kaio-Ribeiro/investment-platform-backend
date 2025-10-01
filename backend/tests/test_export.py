import pytest
from fastapi.testclient import TestClient

def test_unauthorized_export_access(client: TestClient):
    response = client.get("/export/clients/csv")
    assert response.status_code == 403
    
    response = client.get("/export/allocations/csv")
    assert response.status_code == 403
    
    response = client.get("/export/movements/csv")
    assert response.status_code == 403