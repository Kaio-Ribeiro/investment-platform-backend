import pytest
from fastapi.testclient import TestClient
from datetime import date

def test_create_allocation(client: TestClient, auth_headers, test_client_model, test_asset):
    response = client.post(
        "/allocations/",
        json={
            "client_id": test_client_model.id,
            "asset_id": test_asset.id,
            "quantity": 10.5,
            "buy_price": 150.25,
            "buy_date": "2023-01-15"
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["client_id"] == test_client_model.id
    assert data["asset_id"] == test_asset.id
    assert float(data["quantity"]) == 10.5
    assert float(data["buy_price"]) == 150.25

def test_get_allocations(client: TestClient, auth_headers, test_client_model, test_asset):
    # First create an allocation
    client.post(
        "/allocations/",
        json={
            "client_id": test_client_model.id,
            "asset_id": test_asset.id,
            "quantity": 5.0,
            "buy_price": 100.0,
            "buy_date": "2023-01-15"
        },
        headers=auth_headers
    )
    
    response = client.get("/allocations/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["client_name"] == test_client_model.name
    assert data[0]["asset_ticker"] == test_asset.ticker

def test_get_allocations_by_client(client: TestClient, auth_headers, test_client_model, test_asset):
    # First create an allocation
    client.post(
        "/allocations/",
        json={
            "client_id": test_client_model.id,
            "asset_id": test_asset.id,
            "quantity": 5.0,
            "buy_price": 100.0,
            "buy_date": "2023-01-15"
        },
        headers=auth_headers
    )
    
    response = client.get(f"/allocations/?client_id={test_client_model.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["client_id"] == test_client_model.id

def test_get_total_allocation(client: TestClient, auth_headers, test_client_model, test_asset):
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
    
    response = client.get("/allocations/total-allocation", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_allocation" in data
    assert float(data["total_allocation"]) >= 1000.0

def test_get_client_allocation(client: TestClient, auth_headers, test_client_model, test_asset):
    # First create an allocation
    client.post(
        "/allocations/",
        json={
            "client_id": test_client_model.id,
            "asset_id": test_asset.id,
            "quantity": 5.0,
            "buy_price": 200.0,
            "buy_date": "2023-01-15"
        },
        headers=auth_headers
    )
    
    response = client.get(f"/allocations/client/{test_client_model.id}/allocation", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["client_id"] == test_client_model.id
    assert float(data["total_allocation"]) >= 1000.0

def test_create_allocation_invalid_client(client: TestClient, auth_headers, test_asset):
    response = client.post(
        "/allocations/",
        json={
            "client_id": 99999,  # Non-existent client
            "asset_id": test_asset.id,
            "quantity": 10.0,
            "buy_price": 100.0,
            "buy_date": "2023-01-15"
        },
        headers=auth_headers
    )
    assert response.status_code == 404

def test_unauthorized_access(client: TestClient):
    response = client.get("/allocations/")
    assert response.status_code == 401