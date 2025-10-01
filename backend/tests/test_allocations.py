import pytest
from fastapi.testclient import TestClient
from datetime import date

def test_unauthorized_access(client: TestClient):
    response = client.get("/allocations/")
    assert response.status_code == 403

def test_total_allocation_endpoint_exists(client: TestClient):
    response = client.get("/allocations/total-allocation")
    assert response.status_code == 403

def test_create_allocation(client, auth_headers, test_client_model, test_asset):
    """Test creating a new allocation with authentication"""
    allocation_data = {
        "client_id": test_client_model.id,
        "asset_id": test_asset.id,
        "quantity": 100.0,
        "buy_price": 50.0,
        "buy_date": date.today().isoformat()
    }
    response = client.post("/allocations/", json=allocation_data, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["client_id"] == test_client_model.id
    assert response.json()["asset_id"] == test_asset.id
    assert response.json()["quantity"] == 100.0

def test_get_allocations(client, auth_headers):
    """Test getting all allocations with authentication"""
    response = client.get("/allocations/", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_allocations_by_client(client, auth_headers, test_client_model, test_asset):
    """Test getting allocations by client ID"""
    # First create an allocation
    allocation_data = {
        "client_id": test_client_model.id,
        "asset_id": test_asset.id,
        "quantity": 50.0,
        "buy_price": 25.0,
        "buy_date": date.today().isoformat()
    }
    client.post("/allocations/", json=allocation_data, headers=auth_headers)
    
    # Then get allocations for this client
    response = client.get(f"/allocations/client/{test_client_model.id}", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1

def test_update_allocation(client, auth_headers, test_client_model, test_asset):
    """Test updating an allocation"""
    # First create an allocation
    allocation_data = {
        "client_id": test_client_model.id,
        "asset_id": test_asset.id,
        "quantity": 75.0,
        "buy_price": 30.0,
        "buy_date": date.today().isoformat()
    }
    create_response = client.post("/allocations/", json=allocation_data, headers=auth_headers)
    allocation_id = create_response.json()["id"]
    
    # Then update it
    update_data = {
        "quantity": 100.0,
        "buy_price": 40.0
    }
    response = client.put(f"/allocations/{allocation_id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["quantity"] == 100.0

def test_delete_allocation(client, auth_headers, test_client_model, test_asset):
    """Test deleting an allocation"""
    # First create an allocation
    allocation_data = {
        "client_id": test_client_model.id,
        "asset_id": test_asset.id,
        "quantity": 25.0,
        "buy_price": 20.0,
        "buy_date": date.today().isoformat()
    }
    create_response = client.post("/allocations/", json=allocation_data, headers=auth_headers)
    allocation_id = create_response.json()["id"]
    
    # Then delete it
    response = client.delete(f"/allocations/{allocation_id}", headers=auth_headers)
    assert response.status_code == 200
    
    # Verify allocation is deleted
    response = client.get(f"/allocations/{allocation_id}", headers=auth_headers)
    assert response.status_code == 404

def test_total_allocation_with_auth(client, auth_headers):
    """Test getting total allocation value with authentication"""
    response = client.get("/allocations/total-allocation", headers=auth_headers)
    assert response.status_code == 200
    assert "total_allocation" in response.json()