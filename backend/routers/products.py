from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import SessionLocal
from services.product_service import (
    get_all_products,
    get_product_by_id,
    search_products
)


router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.get("/")
def get_products(
    query: str | None = Query(default=None),
    category: str | None = Query(default=None),
    max_price: float | None = Query(default=None),
    db: Session = Depends(get_db)
):
    return search_products(
        db=db,
        query=query,
        category=category,
        max_price=max_price
    )


@router.get("/{product_id}")
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = get_product_by_id(
        db,
        product_id
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return product