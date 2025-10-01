import pytest
from fastapi.testclient import TestClient

def test_unauthorized_access(client: TestClient):
    response = client.get("/assets/")
    assert response.status_code == 403

def test_search_yahoo_endpoint_exists(client: TestClient):
    # Test that the endpoint exists (will fail auth, but endpoint is there)
    response = client.get("/assets/search-yahoo/AAPL")
    assert response.status_code == 403  # Unauthorized, but endpoint exists

def test_create_asset(client, auth_headers):
    """Test creating a new asset with authentication"""
    asset_data = {
        "ticker": "MSFT",
        "name": "Microsoft Corporation",
        "exchange": "NASDAQ",
        "currency": "USD"
    }
    response = client.post("/assets/", json=asset_data, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["ticker"] == "MSFT"
    assert response.json()["name"] == "Microsoft Corporation"

def test_get_assets(client, auth_headers, test_asset):
    """Test getting all assets with authentication"""
    response = client.get("/assets/", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1

def test_get_asset_by_id(client, auth_headers, test_asset):
    """Test getting a specific asset by ID"""
    response = client.get(f"/assets/{test_asset.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == test_asset.id
    assert response.json()["ticker"] == test_asset.ticker

def test_update_asset(client, auth_headers, test_asset):
    """Test updating an asset"""
    update_data = {
        "ticker": test_asset.ticker,
        "name": "Updated Apple Inc.",
        "exchange": test_asset.exchange,
        "currency": test_asset.currency
    }
    response = client.put(f"/assets/{test_asset.id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Apple Inc."

def test_delete_asset(client, auth_headers, test_asset):
    """Test deleting an asset"""
    response = client.delete(f"/assets/{test_asset.id}", headers=auth_headers)
    assert response.status_code == 200
    
    # Verify asset is deleted
    response = client.get(f"/assets/{test_asset.id}", headers=auth_headers)
    assert response.status_code == 404

def test_get_asset_price(client, auth_headers, test_asset):
    """Test getting asset price from Yahoo Finance integration"""
    response = client.get(f"/assets/{test_asset.id}/price", headers=auth_headers)
    # This might fail if Yahoo Finance is down, so we test for either success or service unavailable
    assert response.status_code in [200, 503]

def test_search_yahoo_with_auth(client, auth_headers):
    """Test Yahoo Finance search with authentication"""
    response = client.get("/assets/search-yahoo/AAPL", headers=auth_headers)
    # Test for success or service unavailable (Yahoo Finance might be down)
    assert response.status_code in [200, 503]