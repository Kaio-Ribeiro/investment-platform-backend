import pytest
from fastapi.testclient import TestClient
import csv
import io

def test_unauthorized_export_access(client: TestClient):
    response = client.get("/export/clients/csv")
    assert response.status_code == 403
    
    response = client.get("/export/allocations/csv")
    assert response.status_code == 403
    
    response = client.get("/export/movements/csv")
    assert response.status_code == 403

def test_export_clients_csv(client, auth_headers, test_client_model):
    """Test exporting clients to CSV with authentication"""
    response = client.get("/export/clients/csv", headers=auth_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    
    # Verify CSV content
    csv_content = response.content.decode('utf-8')
    csv_reader = csv.reader(io.StringIO(csv_content))
    headers = next(csv_reader)
    assert "ID" in headers
    assert "Name" in headers
    assert "Email" in headers

def test_export_assets_csv(client, auth_headers, test_asset):
    """Test exporting assets to CSV with authentication"""
    response = client.get("/export/assets/csv", headers=auth_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    
    # Verify CSV content
    csv_content = response.content.decode('utf-8')
    csv_reader = csv.reader(io.StringIO(csv_content))
    headers = next(csv_reader)
    assert "ID" in headers
    assert "Ticker" in headers
    assert "Name" in headers

def test_export_allocations_csv(client, auth_headers, test_client_model, test_asset):
    """Test exporting allocations to CSV with authentication"""
    from datetime import date
    
    # First create an allocation
    allocation_data = {
        "client_id": test_client_model.id,
        "asset_id": test_asset.id,
        "quantity": 100.0,
        "buy_price": 50.0,
        "buy_date": date.today().isoformat()
    }
    client.post("/allocations/", json=allocation_data, headers=auth_headers)

    # Then export allocations
    response = client.get("/export/allocations/csv", headers=auth_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"

    # Verify CSV content
    csv_content = response.content.decode('utf-8')
    csv_reader = csv.reader(io.StringIO(csv_content))
    headers = next(csv_reader)
    assert "ID" in headers
    assert "Client" in headers
    assert "Asset Ticker" in headers

def test_export_movements_csv(client, auth_headers, test_client_model):
    """Test exporting movements to CSV with authentication"""
    from datetime import date

    # First create a movement
    movement_data = {
        "client_id": test_client_model.id,
        "type": "deposit",
        "amount": 1500.0,
        "date": date.today().isoformat(),
        "note": "Test movement"
    }
    client.post("/movements/", json=movement_data, headers=auth_headers)

    # Then export movements
    response = client.get("/export/movements/csv", headers=auth_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"

    # Verify CSV content
    csv_content = response.content.decode('utf-8')
    csv_reader = csv.reader(io.StringIO(csv_content))
    headers = next(csv_reader)
    assert "ID" in headers
    assert "Client" in headers
    assert "Type" in headers