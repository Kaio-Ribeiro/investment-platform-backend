import pytest
from fastapi.testclient import TestClient
from datetime import date

def test_create_movement(client: TestClient, auth_headers, test_client_model):
    response = client.post(
        "/movements/",
        json={
            "client_id": test_client_model.id,
            "type": "deposit",
            "amount": 1000.0,
            "date": "2023-01-15",
            "note": "Initial deposit"
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["client_id"] == test_client_model.id
    assert data["type"] == "deposit"
    assert float(data["amount"]) == 1000.0
    assert data["note"] == "Initial deposit"

def test_get_movements(client: TestClient, auth_headers, test_client_model):
    # First create a movement
    client.post(
        "/movements/",
        json={
            "client_id": test_client_model.id,
            "type": "deposit",
            "amount": 500.0,
            "date": "2023-01-15"
        },
        headers=auth_headers
    )
    
    response = client.get("/movements/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["client_name"] == test_client_model.name

def test_get_movements_by_client(client: TestClient, auth_headers, test_client_model):
    # First create a movement
    client.post(
        "/movements/",
        json={
            "client_id": test_client_model.id,
            "type": "withdrawal",
            "amount": 200.0,
            "date": "2023-01-16"
        },
        headers=auth_headers
    )
    
    response = client.get(f"/movements/?client_id={test_client_model.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["client_id"] == test_client_model.id

def test_get_movements_by_date_range(client: TestClient, auth_headers, test_client_model):
    # First create a movement
    client.post(
        "/movements/",
        json={
            "client_id": test_client_model.id,
            "type": "deposit",
            "amount": 750.0,
            "date": "2023-01-20"
        },
        headers=auth_headers
    )
    
    response = client.get("/movements/?start_date=2023-01-01&end_date=2023-01-31", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1

def test_get_total_captation(client: TestClient, auth_headers, test_client_model):
    # Create some movements
    client.post(
        "/movements/",
        json={
            "client_id": test_client_model.id,
            "type": "deposit",
            "amount": 1000.0,
            "date": "2023-01-15"
        },
        headers=auth_headers
    )
    
    client.post(
        "/movements/",
        json={
            "client_id": test_client_model.id,
            "type": "withdrawal",
            "amount": 200.0,
            "date": "2023-01-16"
        },
        headers=auth_headers
    )
    
    response = client.get("/movements/captation-total", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_deposits" in data
    assert "total_withdrawals" in data
    assert "net_captation" in data

def test_get_captation_by_client(client: TestClient, auth_headers, test_client_model):
    # Create some movements
    client.post(
        "/movements/",
        json={
            "client_id": test_client_model.id,
            "type": "deposit",
            "amount": 2000.0,
            "date": "2023-01-15"
        },
        headers=auth_headers
    )
    
    response = client.get("/movements/captation-by-client", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["client_id"] == test_client_model.id
    assert data[0]["client_name"] == test_client_model.name

def test_create_movement_invalid_client(client: TestClient, auth_headers):
    response = client.post(
        "/movements/",
        json={
            "client_id": 99999,  # Non-existent client
            "type": "deposit",
            "amount": 1000.0,
            "date": "2023-01-15"
        },
        headers=auth_headers
    )
    assert response.status_code == 404

def test_unauthorized_access(client: TestClient):
    response = client.get("/movements/")
    assert response.status_code == 401