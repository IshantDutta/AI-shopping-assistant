import os
import httpx
from dotenv import load_dotenv

load_dotenv()


def search_google_shopping(query: str, max_price: float | None = None, limit: int = 12):
    """
    Optional live shopping retrieval through SerpApi's Google Shopping engine.
    Requires SERPAPI_API_KEY. Without it, returns [] and the app uses its local catalog.
    Prices/availability are provider snapshots and should be verified at the merchant.
    """
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        return []

    params = {
        "engine": "google_shopping",
        "q": query,
        "api_key": api_key,
        "gl": os.getenv("SERPAPI_COUNTRY", "in"),
        "hl": os.getenv("SERPAPI_LANGUAGE", "en"),
    }
    location = os.getenv("SERPAPI_LOCATION")
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
    except (httpx.HTTPError, ValueError):
        return []

    results = []
    for item in payload.get("shopping_results", [])[:limit]:
        price = item.get("extracted_price")
        if price is None:
            # Keep unparsed prices visible as text only; don't pretend they are numeric.
            price = None
        if max_price is not None and price is not None and float(price) > max_price:
            continue
        results.append({
            "id": None,
            "name": item.get("title") or "Product",
            "brand": item.get("source") or "Online merchant",
            "category": "Live search",
            "price": float(price) if price is not None else 0,
            "price_label": item.get("price") or "Price unavailable",
            "rating": item.get("rating"),
            "description": item.get("snippet") or item.get("tag") or "Live Google Shopping result.",
            "image_url": item.get("thumbnail"),
            "product_url": item.get("product_link") or item.get("link"),
            "source": "live",
        })
    return results
