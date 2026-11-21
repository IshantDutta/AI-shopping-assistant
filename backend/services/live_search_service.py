import logging
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_DIR / ".env")
logger = logging.getLogger(__name__)


class LiveSearchError(Exception):
    """Raised when the configured live shopping provider cannot return results."""


def is_live_search_configured() -> bool:
    return bool(os.getenv("SERPAPI_API_KEY", "").strip())


def search_google_shopping(
    query: str,
    max_price: float | None = None,
    limit: int = 12,
) -> list[dict]:
    """
    Optional live Google Shopping retrieval through SerpApi.
    Provider prices and availability are snapshots; verify them at the merchant.
    """
    api_key = os.getenv("SERPAPI_API_KEY", "").strip()
    if not api_key:
        return []

    params = {
        "engine": "google_shopping",
        "q": query,
        "api_key": api_key,
        "gl": os.getenv("SERPAPI_COUNTRY", "in"),
        "hl": os.getenv("SERPAPI_LANGUAGE", "en"),
    }
    location = os.getenv("SERPAPI_LOCATION", "").strip()
    if location:
        params["location"] = location

    try:
        response = httpx.get(
            "https://serpapi.com/search.json",
            params=params,
            timeout=20.0,
        )
        response.raise_for_status()
        payload = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        logger.exception("Live shopping search failed: %s", type(exc).__name__)
        raise LiveSearchError(
            f"Live shopping provider request failed ({type(exc).__name__})."
        ) from exc

    results = []
    for item in payload.get("shopping_results", [])[:limit]:
        raw_price = item.get("extracted_price")
        try:
            price = float(raw_price) if raw_price is not None else None
        except (TypeError, ValueError):
            price = None

        if max_price is not None and price is not None and price > max_price:
            continue

        results.append({
            "id": None,
            "name": item.get("title") or "Product",
            "brand": item.get("source") or "Online merchant",
            "category": "Live search",
            "price": price,
            "price_label": item.get("price") or "Price unavailable",
            "rating": item.get("rating"),
            "description": item.get("snippet") or item.get("tag") or "Live shopping result. Verify details with the seller.",
            "image_url": item.get("thumbnail"),
            "product_url": item.get("product_link") or item.get("link"),
            "source": "live",
        })
    return results
