from sqlalchemy import or_
from sqlalchemy.orm import Session
from models import Product

STOP_WORDS = {
    "the", "and", "for", "with", "under", "over", "below", "above",
    "need", "want", "find", "show", "best", "good", "suggest", "recommend",
    "please", "me", "a", "an", "to", "in", "on", "my", "is", "are",
    "wireless", "budget", "price", "buy", "shopping",
}


def search_catalog(db: Session, query: str | None = None,
                   category: str | None = None,
                   max_price: float | None = None,
                   min_rating: float | None = None):
    q = db.query(Product)

    if query:
        # Match useful words individually so a natural-language request such as
        # "I need headphones under 5000 for gaming" can find category records.
        terms = [
            word.strip(".,!?₹$()[]{}").lower()
            for word in query.split()
        ]
        terms = [word for word in terms if len(word) >= 3 and word not in STOP_WORDS and not word.isdigit()]
        if terms:
            conditions = []
            for term in terms[:8]:
                pattern = f"%{term}%"
                conditions.extend([
                    Product.name.ilike(pattern),
                    Product.brand.ilike(pattern),
                    Product.category.ilike(pattern),
                    Product.description.ilike(pattern),
                ])
            q = q.filter(or_(*conditions))

    if category:
        q = q.filter(Product.category.ilike(f"%{category.strip()}%"))
    if max_price is not None:
        q = q.filter(Product.price <= max_price)
    if min_rating is not None:
        q = q.filter(Product.rating >= min_rating)
    return q.order_by(Product.rating.desc().nullslast(), Product.price.asc()).all()


def get_product(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()


def rank_products(products: list[dict], max_price: float | None = None):
    """Simple transparent ranking: rating first, then budget fit/value."""
    def score(p):
        rating = float(p.get("rating") or 0)
        price = float(p.get("price") or 0)
        budget_score = 1.0
        if max_price and max_price > 0:
            budget_score = max(0.0, 1 - (price / max_price) * 0.25)
        return (rating / 5.0) * 0.8 + budget_score * 0.2
    return sorted(products, key=score, reverse=True)
