from sqlalchemy.orm import Session
from models import Product


def get_all_products(db: Session):
    return db.query(Product).all()


def get_product_by_id(db: Session, product_id: int):
    return (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )


def search_products(
    db: Session,
    query: str | None = None,
    category: str | None = None,
    max_price: float | None = None
):
    products = db.query(Product)

    if query:
        search_text = f"%{query.lower()}%"

        products = products.filter(
            (
                Product.name.ilike(search_text)
                | Product.brand.ilike(search_text)
                | Product.description.ilike(search_text)
            )
        )

    if category:
        products = products.filter(
            Product.category.ilike(f"%{category}%")
        )

    if max_price is not None:
        products = products.filter(
            Product.price <= max_price
        )

    return products.order_by(Product.rating.desc()).all()