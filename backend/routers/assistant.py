from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from schemas import ChatRequest, CompareRequest
from services.product_service import search_catalog
from services.live_search_service import search_google_shopping
from services.recommendation_service import recommend
from services.ai_service import generate_shopping_advice

router = APIRouter(prefix="/assistant", tags=["AI Assistant"])


@router.post("/chat")
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    catalog_rows = search_catalog(
        db,
        query=request.message,
        category=request.category,
        max_price=request.max_price,
    )
    catalog = [{
        "id": p.id, "name": p.name, "brand": p.brand, "category": p.category,
        "price": p.price, "price_label": f"₹{p.price:,.0f}",
        "rating": p.rating, "description": p.description,
        "image_url": p.image_url, "product_url": p.product_url, "source": "catalog",
    } for p in catalog_rows]

    live = []
    if request.use_live_search:
        live = search_google_shopping(request.message, request.max_price)

    # Hybrid: catalog and live results are both returned, with source clearly identified.
    combined = catalog + live
    ranked = recommend(combined, request.max_price, limit=12)
    answer = generate_shopping_advice(request.message, ranked)
    return {
        "message": answer,
        "products": ranked,
        "sources": {
            "catalog_count": len(catalog),
            "live_count": len(live),
            "live_search_configured": bool(__import__("os").getenv("SERPAPI_API_KEY")),
        },
    }


@router.post("/compare")
def compare_products(request: CompareRequest, db: Session = Depends(get_db)):
    from models import Product
    rows = db.query(Product).filter(Product.id.in_(request.product_ids)).all()
    return {
        "products": [{
            "id": p.id, "name": p.name, "brand": p.brand, "category": p.category,
            "price": p.price, "rating": p.rating, "description": p.description,
        } for p in rows]
    }
