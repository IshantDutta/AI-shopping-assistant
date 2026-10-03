from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import SessionLocal
from services.product_service import search_products
from services.ai_service import generate_shopping_response


router = APIRouter(
    prefix="/assistant",
    tags=["AI Assistant"]
)


class ShoppingRequest(BaseModel):
    message: str
    max_price: float | None = None
    category: str | None = None


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post("/chat")
def shopping_assistant(
    request: ShoppingRequest,
    db: Session = Depends(get_db)
):
    """
    Main endpoint for the AI shopping assistant.
    """

    # Search our product database
    products = search_products(
        db=db,
        query=request.message,
        category=request.category,
        max_price=request.max_price
    )

    # Send matching products to the AI
    result = generate_shopping_response(
        user_message=request.message,
        products=products[:10]
    )

    return result