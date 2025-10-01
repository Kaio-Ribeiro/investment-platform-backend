import pytest
from fastapi.testclient import TestClient

def test_export_clients_csv(client: TestClient, auth_headers, test_client_model):
    response = client.get("/export/clients/csv", headers=auth_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "attachment; filename=clients.csv" in response.headers["content-disposition"]
    
    # Check CSV content
    content = response.text
    assert "ID,Name,Email,Status,Created At" in content
    assert test_client_model.name in content

def test_export_allocations_csv(client: TestClient, auth_headers, test_client_model, test_asset):
    # First create an allocation
    client.post(
        "/allocations/",
        json={
            "client_id": test_client_model.id,
            "asset_id": test_asset.id,
            "quantity": 10.0,
            "buy_price": 100.0,
            "buy_date": "2023-01-15"
        },
        headers=auth_headers
    )
    
    response = client.get("/export/allocations/csv", headers=auth_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "attachment; filename=allocations.csv" in response.headers["content-disposition"]
    
    # Check CSV content
    content = response.text
    assert "ID,Client,Asset Ticker,Asset Name" in content
    assert test_client_model.name in content
    assert test_asset.ticker in content

def test_export_movements_csv(client: TestClient, auth_headers, test_client_model):
    # First create a movement
    client.post(
        "/movements/",
        json={
            "client_id": test_client_model.id,
            "type": "deposit",
            "amount": 1000.0,
            "date": "2023-01-15",
            "note": "Test deposit"
        },
        headers=auth_headers
    )
    
    response = client.get("/export/movements/csv", headers=auth_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "attachment; filename=movements.csv" in response.headers["content-disposition"]
    
    # Check CSV content
    content = response.text
    assert "ID,Client,Type,Amount,Date,Note" in content
    assert test_client_model.name in content
    assert "deposit" in content
    assert "1000" in content

def test_export_movements_csv_with_date_filter(client: TestClient, auth_headers, test_client_model):
    # First create a movement
    client.post(
        "/movements/",
        json={
            "client_id": test_client_model.id,
            "type": "withdrawal",
            "amount": 500.0,
            "date": "2023-01-20"
        },
        headers=auth_headers
    )
    
    response = client.get(
        "/export/movements/csv?start_date=2023-01-01&end_date=2023-01-31", 
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    
    # Check CSV content
    content = response.text
    assert "withdrawal" in content

def test_unauthorized_export_access(client: TestClient):
    response = client.get("/export/clients/csv")
    assert response.status_code == 401
    
    response = client.get("/export/allocations/csv")
    assert response.status_code == 401
    
    response = client.get("/export/movements/csv")
    assert response.status_code == 401