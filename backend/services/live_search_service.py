
import logging
import os
from pathlib import Path
from urllib.parse import urlparse

import httpx
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_DIR / ".env")

logger = logging.getLogger(__name__)

SERPAPI_URL = "https://serpapi.com/search.json"
MAX_PRODUCT_LOOKUPS = 6


class LiveSearchError(Exception):
    """Raised when the configured live shopping provider cannot return results."""


def is_live_search_configured() -> bool:
    return bool(os.getenv("SERPAPI_API_KEY", "").strip())


def _serpapi_request(params: dict) -> dict:
    """Send a request to SerpApi and validate its response."""
    response = httpx.get(
        SERPAPI_URL,
        params=params,
        timeout=25.0,
    )
    response.raise_for_status()

    payload = response.json()

    if payload.get("error"):
        raise LiveSearchError(str(payload["error"]))

    return payload


def _is_direct_merchant_url(url: str | None) -> bool:
    """Reject Google, SerpApi and non-HTTP links."""
    if not url:
        return False

    try:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()

        if parsed.scheme not in {"http", "https"}:
            return False

        blocked_hosts = (
            "google.com",
            "www.google.com",
            "shopping.google.com",
            "serpapi.com",
        )

        return not any(
            host == blocked or host.endswith("." + blocked)
            for blocked in blocked_hosts
        )
    except ValueError:
        return False


def _get_merchant_offers(
    product_id: str,
    api_key: str,
) -> list[dict]:
    """Retrieve real merchant offers for one Google Shopping product."""
    params = {
        "engine": "google_product",
        "product_id": product_id,
        "offer_view": "true",
        "api_key": api_key,
        "gl": os.getenv("SERPAPI_COUNTRY", "in"),
        "hl": os.getenv("SERPAPI_LANGUAGE", "en"),
    }

    payload = _serpapi_request(params)
    product = payload.get("product_results") or {}

    offers = []

    for store in product.get("stores", []):
        merchant_url = store.get("link")

        if not _is_direct_merchant_url(merchant_url):
            continue

        raw_price = store.get("extracted_price")

        try:
            price = float(raw_price) if raw_price is not None else None
        except (TypeError, ValueError):
            price = None

        offers.append({
            "merchant": store.get("name") or "Online merchant",
            "price": price,
            "price_label": store.get("price") or "Price unavailable",
            "product_url": merchant_url,
            "shipping": store.get("shipping"),
            "availability": store.get("details_and_offers", []),
            "condition": store.get("condition"),
        })

    # Cheapest known merchant offer first.
    offers.sort(
        key=lambda offer: (
            offer["price"] is None,
            offer["price"] if offer["price"] is not None else float("inf"),
        )
    )

    return offers


def search_google_shopping(
    query: str,
    max_price: float | None = None,
    limit: int = 12,
) -> list[dict]:
    """
    Search Google Shopping and resolve products to direct merchant offers.

    Prices and availability are provider snapshots. Users should verify
    final price, shipping and stock on the merchant website.
    """
    api_key = os.getenv("SERPAPI_API_KEY", "").strip()

    if not api_key:
        return []

    search_params = {
        "engine": "google_shopping",
        "q": query,
        "api_key": api_key,
        "gl": os.getenv("SERPAPI_COUNTRY", "in"),
        "hl": os.getenv("SERPAPI_LANGUAGE", "en"),
    }

    location = os.getenv("SERPAPI_LOCATION", "").strip()
    if location:
        search_params["location"] = location

    try:
        shopping_payload = _serpapi_request(search_params)
    except (httpx.HTTPError, ValueError, LiveSearchError) as exc:
        logger.exception("Google Shopping search failed")
        raise LiveSearchError(
            f"Shopping search failed ({type(exc).__name__})."
        ) from exc

    shopping_items = shopping_payload.get("shopping_results", [])
    results = []
    lookup_count = 0

    for item in shopping_items:
        if len(results) >= limit:
            break

        product_id = item.get("product_id")

        if not product_id:
            continue

        # Use the Shopping price as an initial budget filter.
        raw_search_price = item.get("extracted_price")

        try:
            search_price = (
                float(raw_search_price)
                if raw_search_price is not None
                else None
            )
        except (TypeError, ValueError):
            search_price = None

        if max_price is not None:
            if search_price is None or search_price > max_price:
                continue

        # Keep SerpApi usage controlled.
        if lookup_count >= MAX_PRODUCT_LOOKUPS:
            break

        lookup_count += 1

        try:
            offers = _get_merchant_offers(
                str(product_id),
                api_key,
            )
        except (httpx.HTTPError, ValueError, LiveSearchError) as exc:
            logger.warning(
                "Could not resolve merchant offers for product %s: %s",
                product_id,
                type(exc).__name__,
            )
            continue

        # Do not advertise a Google redirect as a direct purchase link.
        if not offers:
            continue

        # Choose the cheapest known seller offer.
        best_offer = offers[0]

        offer_price = best_offer["price"]

        if max_price is not None:
            if offer_price is None or offer_price > max_price:
                continue

        description_parts = [
            "Live Google Shopping result.",
            f"Merchant: {best_offer['merchant']}.",
        ]

        if best_offer.get("shipping"):
            description_parts.append(
                f"Shipping: {best_offer['shipping']}."
            )

        if best_offer.get("condition"):
            description_parts.append(
                f"Condition: {best_offer['condition']}."
            )

        results.append({
            "id": None,
            "name": item.get("title") or "Product",
            "brand": best_offer["merchant"],
            "category": "Live search",
            "price": offer_price,
            "price_label": best_offer["price_label"],
            "rating": item.get("rating"),
            "description": " ".join(description_parts),
            "image_url": item.get("thumbnail"),
            "product_url": best_offer["product_url"],
            "source": "live",
        })

    return results
