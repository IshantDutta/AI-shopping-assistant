from fastapi.testclient import TestClient

from main import app
from services.comparison_service import build_comparison
from services.live_search_service import _availability_status


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_product_catalog_endpoint_returns_products():
    response = client.get("/products/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1


def test_compare_endpoint_accepts_product_objects():
    payload = {
        "products": [
            {
                "name": "Test in-stock product",
                "brand": "Test Store",
                "category": "Earbuds",
                "price": 1000,
                "rating": 4.5,
                "availability_status": "in_stock",
                "source": "live",
            },
            {
                "name": "Test out-of-stock product",
                "brand": "Another Store",
                "category": "Earbuds",
                "price": 500,
                "rating": 5.0,
                "availability_status": "out_of_stock",
                "source": "live",
            },
        ]
    }
    response = client.post("/assistant/compare", json=payload)
    assert response.status_code == 200
    result = response.json()
    assert result["summary"]["best_value_name"] == "Test in-stock product"
    assert result["summary"]["scores"][1]["eligible"] is False


def test_comparison_never_selects_out_of_stock_product():
    result = build_comparison([
        {"name": "Available", "price": 1500, "rating": 4.2, "availability_status": "in_stock"},
        {"name": "Cheapest but unavailable", "price": 100, "rating": 5.0, "availability_status": "out_of_stock"},
    ])
    assert result["summary"]["best_value_name"] == "Available"


def test_unknown_availability_is_not_assumed_in_stock():
    result = build_comparison([
        {"name": "Unknown", "price": 100, "rating": 5.0, "availability_status": "unknown"},
    ])
    assert result["summary"]["best_value_name"] is None
    assert result["summary"]["scores"][0]["eligible"] is False


def test_availability_parser_detects_out_of_stock():
    status, _ = _availability_status(["Out of stock online"])
    assert status == "out_of_stock"


def test_availability_parser_detects_in_stock():
    status, _ = _availability_status(["In stock"])
    assert status == "in_stock"


def test_availability_parser_does_not_guess_when_missing():
    status, _ = _availability_status([])
    assert status == "unknown"
