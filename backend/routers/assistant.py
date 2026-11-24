import logging

from fastapi import APIRouter, Depends
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
from services.comparison_service import build_comparison

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/assistant", tags=["AI Assistant"])


@router.post("/chat")
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    # Use an explicit budget from the UI first; otherwise parse it from the message.
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
        "availability_status": "unknown",
        "availability_details": [],
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


@router.post("/compare")
def compare_products(request: CompareRequest, db: Session = Depends(get_db)):
    # The frontend sends complete selected product objects so live products
    # (which have no local database ID) can be compared too.
    submitted = [product.model_dump() for product in request.products]

    # Refresh catalogue records from the database when IDs are available.
    ids = [product["id"] for product in submitted if product.get("id") is not None]
    rows = db.query(Product).filter(Product.id.in_(ids)).all() if ids else []
    by_id = {product.id: product for product in rows}

    products = []
    for item in submitted:
        db_product = by_id.get(item.get("id"))
        if db_product:
            item.update({
                "name": db_product.name,
                "brand": db_product.brand,
                "category": db_product.category,
                "price": db_product.price,
                "rating": db_product.rating,
                "description": db_product.description,
                "image_url": db_product.image_url,
                "product_url": db_product.product_url,
                "source": "catalog",
            })
        products.append(item)

    return build_comparison(products)


@router.get("/status")
def assistant_status():
    return {
        "ai_provider": "Gemini",
        "ai_configured": is_gemini_configured(),
        "ai_model": get_gemini_model(),
        "live_search_configured": is_live_search_configured(),
    }
