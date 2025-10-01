import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

def test_get_assets(client: TestClient, auth_headers, test_asset):
    response = client.get("/assets/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["ticker"] == "AAPL"

def test_create_asset(client: TestClient, auth_headers):
    response = client.post(
        "/assets/",
        json={
            "ticker": "GOOGL",
            "name": "Alphabet Inc.",
            "exchange": "NASDAQ",
            "currency": "USD"
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "GOOGL"
    assert data["name"] == "Alphabet Inc."

def test_get_asset_by_id(client: TestClient, auth_headers, test_asset):
    response = client.get(f"/assets/{test_asset.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "AAPL"
    assert data["name"] == "Apple Inc."

@patch('app.services.yahoo_finance.yahoo_finance.search_asset')
def test_search_yahoo_asset(mock_search, client: TestClient, auth_headers):
    mock_search.return_value = {
        "ticker": "MSFT",
        "name": "Microsoft Corporation",
        "exchange": "NASDAQ",
        "currency": "USD"
    }
    
    response = client.get("/assets/search-yahoo/MSFT", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "MSFT"
    assert data["name"] == "Microsoft Corporation"

@patch('app.services.yahoo_finance.yahoo_finance.search_asset')
def test_create_asset_from_yahoo(mock_search, client: TestClient, auth_headers):
    mock_search.return_value = {
        "ticker": "TSLA",
        "name": "Tesla, Inc.",
        "exchange": "NASDAQ",
        "currency": "USD"
    }
    
    response = client.post("/assets/from-yahoo/TSLA", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "TSLA"
    assert data["name"] == "Tesla, Inc."

def test_duplicate_ticker_error(client: TestClient, auth_headers, test_asset):
    response = client.post(
        "/assets/",
        json={
            "ticker": "AAPL",  # Already exists
            "name": "Apple Inc.",
            "exchange": "NASDAQ",
            "currency": "USD"
        },
        headers=auth_headers
    )
    assert response.status_code == 400

def test_unauthorized_access(client: TestClient):
    response = client.get("/assets/")
    assert response.status_code == 401