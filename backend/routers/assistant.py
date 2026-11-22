import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Product
from schemas import ChatRequest, CompareRequest
from services.ai_service import (
    generate_shopping_advice,
    get_gemini_model,
    is_gemini_configured,
)
from services.live_search_service import (
    LiveSearchError,
    is_live_search_configured,
    search_google_shopping,
)
from services.product_service import extract_budget, search_catalog
from services.recommendation_service import recommend

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/assistant", tags=["AI Assistant"])


@router.post("/chat")
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    budget = request.max_price
    if budget is None:
        budget = extract_budget(request.message)

    catalog_rows = search_catalog(
        db,
        query=request.message,
        category=request.category,
        max_price=budget,
    )

    catalog = [{
        "id": product.id,
        "name": product.name,
        "brand": product.brand,
        "category": product.category,
        "price": product.price,
        "price_label": f"₹{product.price:,.0f}",
        "rating": product.rating,
        "description": product.description,
        "image_url": product.image_url,
        "product_url": product.product_url,
        "source": "catalog",
    } for product in catalog_rows]

    live = []
    live_error = None
    if request.use_live_search and is_live_search_configured():
        try:
            live = search_google_shopping(request.message, budget)
        except LiveSearchError as exc:
            live_error = str(exc)
            logger.warning("%s", live_error)

    combined = catalog + live
    ranked = recommend(combined, budget, limit=12)
    answer = generate_shopping_advice(request.message, ranked)

    return {
        "message": answer,
        "products": ranked,
        "sources": {
            "catalog_count": len(catalog),
            "live_count": len(live),
            "live_search_configured": is_live_search_configured(),
            "live_search_error": live_error,
            "ai_provider": "Gemini",
            "ai_configured": is_gemini_configured(),
            "ai_model": get_gemini_model(),
        },
        "applied_filters": {
            "max_price": budget,
            "category": request.category,
        },
    }


def _compare_score(product: dict, lowest_price: float | None) -> float | None:
    """Transparent relative score; does not invent missing ratings or prices."""
    price = product.get("price")
    rating = product.get("rating")
    parts = []

    if rating is not None:
        parts.append((0.60, max(0.0, min(float(rating), 5.0)) / 5.0))

    if price is not None and lowest_price is not None and float(price) > 0:
        parts.append((0.40, min(1.0, lowest_price / float(price))))

    if not parts:
        return None

    weight_total = sum(weight for weight, _ in parts)
    return round(100 * sum(weight * value for weight, value in parts) / weight_total, 1)


def _comparison_summary(products: list[dict]) -> dict:
    known_prices = [
        float(p["price"]) for p in products
        if p.get("price") is not None and float(p["price"]) > 0
    ]
    lowest_price = min(known_prices) if known_prices else None

    scored = []
    for index, product in enumerate(products):
        score = _compare_score(product, lowest_price)
        scored.append({
            "index": index,
            "name": product.get("name"),
            "score": score,
        })

    eligible = [item for item in scored if item["score"] is not None]
    best = max(eligible, key=lambda item: item["score"]) if eligible else None

    return {
        "best_value_index": best["index"] if best else None,
        "best_value_name": best["name"] if best else None,
        "scores": scored,
        "method": (
            "Relative score: 60% customer rating and 40% affordability "
            "(lowest listed price compared with the other selected products). "
            "If a rating or price is missing, the score uses only available data."
        ),
        "notice": "Prices, ratings, stock and delivery can change. Verify details with the merchant before buying.",
    }


@router.post("/compare")
def compare_products(request: CompareRequest, db: Session = Depends(get_db)):
    if request.products:
        # Live results are sent as product snapshots because they have no local DB id.
        products = [item.model_dump() for item in request.products]
    else:
        rows = db.query(Product).filter(Product.id.in_(request.product_ids)).all()
        by_id = {product.id: product for product in rows}
        ordered = [
            by_id[product_id]
            for product_id in request.product_ids
            if product_id in by_id
        ]
        if len(ordered) != len(request.product_ids):
            raise HTTPException(status_code=404, detail="One or more catalogue products were not found.")

        products = [{
            "id": product.id,
            "name": product.name,
            "brand": product.brand,
            "category": product.category,
            "price": product.price,
            "price_label": f"₹{product.price:,.0f}" if product.price is not None else None,
            "rating": product.rating,
            "description": product.description,
            "image_url": product.image_url,
            "product_url": product.product_url,
            "source": "catalog",
        } for product in ordered]

    if len(products) < 2:
        raise HTTPException(status_code=422, detail="Select at least two products to compare.")

    return {
        "products": products,
        "summary": _comparison_summary(products),
    }


@router.get("/status")
def assistant_status():
    return {
        "ai_provider": "Gemini",
        "ai_configured": is_gemini_configured(),
        "ai_model": get_gemini_model(),
        "live_search_configured": is_live_search_configured(),
    }
