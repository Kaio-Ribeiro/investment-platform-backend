import pytest
from fastapi.testclient import TestClient
from datetime import date

def test_unauthorized_access(client: TestClient):
    response = client.get("/movements/")
    assert response.status_code == 403

def test_captation_total_endpoint_exists(client: TestClient):
    response = client.get("/movements/captation-total")
    assert response.status_code == 403

def test_create_movement(client, auth_headers, test_client_model):
    """Test creating a new movement with authentication"""
    movement_data = {
        "client_id": test_client_model.id,
        "type": "deposit",
        "amount": 1500.0,
        "date": date.today().isoformat(),
        "note": "Initial deposit"
    }
    response = client.post("/movements/", json=movement_data, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["client_id"] == test_client_model.id
    assert response.json()["type"] == "deposit"
    assert response.json()["amount"] == 1500.0

def test_get_movements(client, auth_headers):
    """Test getting all movements with authentication"""
    response = client.get("/movements/", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_movements_by_client(client, auth_headers, test_client_model):
    """Test getting movements by client ID"""
    # First create a movement
    movement_data = {
        "client_id": test_client_model.id,
        "type": "withdrawal",
        "amount": 800.0,
        "date": date.today().isoformat(),
        "note": "Withdrawal for investment"
    }
    client.post("/movements/", json=movement_data, headers=auth_headers)
    
    # Then get movements for this client
    response = client.get(f"/movements/client/{test_client_model.id}", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1

def test_update_movement(client, auth_headers, test_client_model):
    """Test updating a movement"""
    # First create a movement
    movement_data = {
        "client_id": test_client_model.id,
        "type": "deposit",
        "amount": 2100.0,
        "date": date.today().isoformat(),
        "note": "Initial deposit"
    }
    create_response = client.post("/movements/", json=movement_data, headers=auth_headers)
    movement_id = create_response.json()["id"]
    
    # Then update it
    update_data = {
        "client_id": test_client_model.id,
        "type": "deposit",
        "amount": 2800.0,
        "date": date.today().isoformat(),
        "note": "Updated deposit amount"
    }
    response = client.put(f"/movements/{movement_id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["amount"] == 2800.0

def test_delete_movement(client, auth_headers, test_client_model):
    """Test deleting a movement"""
    # First create a movement
    movement_data = {
        "client_id": test_client_model.id,
        "type": "withdrawal",
        "amount": 1240.0,
        "date": date.today().isoformat(),
        "note": "Test withdrawal"
    }
    create_response = client.post("/movements/", json=movement_data, headers=auth_headers)
    movement_id = create_response.json()["id"]
    
    # Then delete it
    response = client.delete(f"/movements/{movement_id}", headers=auth_headers)
    assert response.status_code == 200
    
    # Verify movement is deleted
    response = client.get(f"/movements/{movement_id}", headers=auth_headers)
    assert response.status_code == 404

def test_captation_total_with_auth(client, auth_headers):
    """Test getting captation total with authentication"""
    response = client.get("/movements/captation-total", headers=auth_headers)
    assert response.status_code == 200
    assert "total_deposits" in response.json()
    assert "total_withdrawals" in response.json()
    assert "net_captation" in response.json()