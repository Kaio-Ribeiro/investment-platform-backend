import pytest
from fastapi.testclient import TestClient

def test_create_client(client: TestClient, auth_headers):
    response = client.post(
        "/clients/",
        json={
            "name": "John Doe",
            "email": "john@example.com",
            "is_active": True
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["email"] == "john@example.com"
    assert data["is_active"] == True

def test_get_clients(client: TestClient, auth_headers, test_client_model):
    response = client.get("/clients/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["name"] == "Test Client"

def test_get_client_by_id(client: TestClient, auth_headers, test_client_model):
    response = client.get(f"/clients/{test_client_model.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Client"
    assert data["email"] == "client@example.com"

def test_update_client(client: TestClient, auth_headers, test_client_model):
    response = client.put(
        f"/clients/{test_client_model.id}",
        json={"name": "Updated Client"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Client"

def test_delete_client(client: TestClient, auth_headers, test_client_model):
    response = client.delete(f"/clients/{test_client_model.id}", headers=auth_headers)
    assert response.status_code == 200

def test_search_clients(client: TestClient, auth_headers, test_client_model):
    response = client.get("/clients/?search=Test", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1

def test_unauthorized_access(client: TestClient):
    response = client.get("/clients/")
    assert response.status_code == 401