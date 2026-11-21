from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from schemas import ProductOut
from services.product_service import get_product, search_catalog

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/", response_model=list[ProductOut])
def list_products(
    query: str | None = None,
    category: str | None = None,
    max_price: float | None = Query(default=None, ge=0),
    min_rating: float | None = Query(default=None, ge=0, le=5),
    db: Session = Depends(get_db),
):
    products = search_catalog(db, query, category, max_price, min_rating)
    return [
        ProductOut.model_validate(product).model_copy(
            update={"source": "catalog", "price_label": f"₹{product.price:,.0f}"}
        )
        for product in products
    ]


@router.get("/{product_id}", response_model=ProductOut)
def product_detail(product_id: int, db: Session = Depends(get_db)):
    product = get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductOut.model_validate(product).model_copy(
        update={"source": "catalog", "price_label": f"₹{product.price:,.0f}"}
    )
