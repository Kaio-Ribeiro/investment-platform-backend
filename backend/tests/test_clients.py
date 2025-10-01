import pytest
from fastapi.testclient import TestClient

def test_unauthorized_access(client: TestClient):
    """Test that client endpoints require authentication"""
    response = client.get("/clients/")
    assert response.status_code == 403  # FastAPI Security returns 403 for missing auth

def test_api_is_running(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Investment API is running!"}

def test_create_client(client, auth_headers):
    """Test creating a new client with authentication"""
    client_data = {
        "name": "New Test Client",
        "email": "newclient@example.com",
        "is_active": True
    }
    response = client.post("/clients/", json=client_data, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "New Test Client"
    assert response.json()["email"] == "newclient@example.com"

def test_get_clients(client, auth_headers, test_client_model):
    """Test getting all clients with authentication"""
    response = client.get("/clients/", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1

def test_get_client_by_id(client, auth_headers, test_client_model):
    """Test getting a specific client by ID"""
    response = client.get(f"/clients/{test_client_model.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == test_client_model.id
    assert response.json()["name"] == test_client_model.name

def test_update_client(client, auth_headers, test_client_model):
    """Test updating a client"""
    update_data = {
        "name": "Updated Client Name",
        "email": test_client_model.email,
        "is_active": True
    }
    response = client.put(f"/clients/{test_client_model.id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Client Name"

def test_delete_client(client, auth_headers, test_client_model):
    """Test deleting a client"""
    response = client.delete(f"/clients/{test_client_model.id}", headers=auth_headers)
    assert response.status_code == 200
    
    # Verify client is deleted
    response = client.get(f"/clients/{test_client_model.id}", headers=auth_headers)
    assert response.status_code == 404