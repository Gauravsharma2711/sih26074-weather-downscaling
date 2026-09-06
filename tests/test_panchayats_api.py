"""
Unit and Integration tests for GET /api/v1/panchayats endpoint.
Tests pagination, block filtering, keyword search, parameter validation,
and OpenAPI documentation compliance.
"""

import pytest


def test_get_panchayats_default_pagination(client):
    """
    Test GET /api/v1/panchayats with default pagination parameters (page=1, page_size=50).
    """
    response = client.get("/api/v1/panchayats")
    assert response.status_code == 200, response.text
    data = response.json()

    # Verify pagination envelope
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "total_pages" in data
    assert "items" in data

    assert data["page"] == 1
    assert data["page_size"] == 50
    assert data["total"] > 0
    assert len(data["items"]) <= 50

    # Verify required schema fields on first item
    first_item = data["items"][0]
    expected_fields = {
        "panchayat_id",
        "lgd_code",
        "panchayat_name",
        "block_name",
        "district_name",
        "latitude",
        "longitude",
        "elevation_m",
    }
    assert set(first_item.keys()) == expected_fields

    # Ensure unwanted internal fields / secrets are NOT exposed
    forbidden_fields = {
        "actual_rainfall_mm",
        "station_id",
        "station_latitude",
        "station_longitude",
        "station_distance_km",
        "forecast_issue_date",
        "date",
        "block_forecast_rainfall_mm",
        "password",
        "database_url",
    }
    for field in forbidden_fields:
        assert field not in first_item


def test_get_panchayats_custom_pagination(client):
    """
    Test GET /api/v1/panchayats with custom page and page_size.
    """
    response = client.get("/api/v1/panchayats?page=2&page_size=10")
    assert response.status_code == 200
    data = response.json()

    assert data["page"] == 2
    assert data["page_size"] == 10
    assert len(data["items"]) == 10


def test_get_panchayats_filter_by_block(client):
    """
    Test filtering Panchayats by block_name (case-insensitive).
    """
    response = client.get("/api/v1/panchayats?block_name=Baglan&page_size=20")
    assert response.status_code == 200
    data = response.json()

    assert data["total"] > 0
    for item in data["items"]:
        assert item["block_name"].lower() == "baglan"


def test_get_panchayats_search_by_name(client):
    """
    Test keyword search matching Panchayat name.
    """
    response = client.get("/api/v1/panchayats?search=Ajmer")
    assert response.status_code == 200
    data = response.json()

    assert data["total"] >= 1
    found_match = any("ajmer" in item["panchayat_name"].lower() for item in data["items"])
    assert found_match


def test_get_panchayats_search_by_lgd_code(client):
    """
    Test keyword search matching LGD code.
    """
    response = client.get("/api/v1/panchayats?search=182597")
    assert response.status_code == 200
    data = response.json()

    assert data["total"] >= 1
    assert any(item["lgd_code"] == 182597 for item in data["items"])


def test_get_panchayats_invalid_page_param(client):
    """
    Test that invalid page (< 1) returns 422 Unprocessable Entity.
    """
    response = client.get("/api/v1/panchayats?page=0")
    assert response.status_code == 422


def test_get_panchayats_invalid_page_size_param(client):
    """
    Test that invalid page_size (> 500 or < 1) returns 422 Unprocessable Entity.
    """
    # Test page_size < 1
    response_low = client.get("/api/v1/panchayats?page_size=0")
    assert response_low.status_code == 422

    # Test page_size > 500
    response_high = client.get("/api/v1/panchayats?page_size=1000")
    assert response_high.status_code == 422


def test_openapi_documentation(client):
    """
    Verify that OpenAPI documentation includes /api/v1/panchayats and /api/v1/panchayats/{panchayat_id} with schema details.
    """
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    spec = response.json()

    assert "/api/v1/panchayats" in spec["paths"]
    panchayats_path = spec["paths"]["/api/v1/panchayats"]
    assert "get" in panchayats_path
    get_spec = panchayats_path["get"]

    assert get_spec["summary"] == "List Nashik District Panchayats"
    param_names = [p["name"] for p in get_spec.get("parameters", [])]
    assert "block_name" in param_names
    assert "search" in param_names
    assert "page" in param_names
    assert "page_size" in param_names

    # Check /api/v1/panchayats/{panchayat_id} documentation
    assert "/api/v1/panchayats/{panchayat_id}" in spec["paths"]
    detail_spec = spec["paths"]["/api/v1/panchayats/{panchayat_id}"]["get"]
    assert detail_spec["summary"] == "Get Panchayat Details by ID"
    detail_param_names = [p["name"] for p in detail_spec.get("parameters", [])]
    assert "panchayat_id" in detail_param_names


def test_get_panchayat_by_id_success(client):
    """
    Test GET /api/v1/panchayats/{panchayat_id} with a valid existing Panchayat ID.
    """
    response = client.get("/api/v1/panchayats/1001")
    assert response.status_code == 200, response.text
    data = response.json()

    assert data["panchayat_id"] == 1001
    assert data["lgd_code"] == 182597
    assert data["panchayat_name"] == "Ajmer Saundane"
    assert data["block_name"] == "Baglan"
    assert data["district_name"] == "Nashik"
    assert isinstance(data["latitude"], float)
    assert isinstance(data["longitude"], float)
    assert isinstance(data["elevation_m"], float)

    # Ensure internal DB fields are not exposed
    forbidden = ["actual_rainfall_mm", "station_id", "forecast_issue_date", "date"]
    for f in forbidden:
        assert f not in data


def test_get_panchayat_by_id_not_found(client):
    """
    Test GET /api/v1/panchayats/{panchayat_id} with a non-existent ID returns 404.
    """
    response = client.get("/api/v1/panchayats/999999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_panchayat_by_id_invalid_id(client):
    """
    Test GET /api/v1/panchayats/{panchayat_id} with invalid ID format or zero returns 422.
    """
    # Test zero (< 1)
    response_zero = client.get("/api/v1/panchayats/0")
    assert response_zero.status_code == 422

    # Test non-integer string
    response_str = client.get("/api/v1/panchayats/invalid_id")
    assert response_str.status_code == 422
