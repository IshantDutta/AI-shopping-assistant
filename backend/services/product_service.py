import re

from sqlalchemy import or_
from sqlalchemy.orm import Session

from models import Product

STOP_WORDS = {
    "the", "and", "for", "with", "under", "over", "below", "above",
    "need", "want", "find", "show", "best", "good", "suggest", "recommend",
    "please", "me", "a", "an", "to", "in", "on", "my", "is", "are",
    "wireless", "budget", "price", "buy", "shopping", "around", "about",
    "less", "than", "rupees", "rs", "₹", "upto", "up", "maximum", "max",
    "minimum", "at", "of", "from", "college", "use", "using", "for",
}


def extract_budget(text: str | None) -> float | None:
    """Extract common Indian/English budget phrases, e.g. under ₹5,000."""
    if not text:
        return None

    patterns = [
        r"(?:under|below|less than|upto|up to|max(?:imum)?)\s*(?:₹|rs\.?|inr)?\s*([\d,]+(?:\.\d+)?)",
        r"(?:₹|rs\.?|inr)\s*([\d,]+(?:\.\d+)?)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            try:
                return float(match.group(1).replace(",", ""))
            except ValueError:
                return None
    return None


def _query_terms(query: str | None) -> list[str]:
    if not query:
        return []
    raw_terms = re.findall(r"[a-zA-Z0-9]+", query.lower())
    terms = [
        term for term in raw_terms
        if len(term) >= 3 and term not in STOP_WORDS and not term.isdigit()
    ]
    # Keep a bounded number of terms to avoid overly broad SQL expressions.
    return list(dict.fromkeys(terms[:8]))


def search_catalog(
    db: Session,
    query: str | None = None,
    category: str | None = None,
    max_price: float | None = None,
    min_rating: float | None = None,
):
    q = db.query(Product)

    terms = _query_terms(query)
    if terms:
        conditions = []
        for term in terms:
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

    return q.order_by(Product.rating.desc(), Product.price.asc()).all()


def get_product(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()


def rank_products(products: list[dict], max_price: float | None = None):
    """Rank products using rating and budget fit; unknown prices are not treated as free."""
    def score(product):
        try:
            rating = float(product.get("rating") or 0)
        except (TypeError, ValueError):
            rating = 0.0

        price_value = product.get("price")
        try:
            price = float(price_value) if price_value is not None else None
        except (TypeError, ValueError):
            price = None

        rating_score = max(0.0, min(rating, 5.0)) / 5.0
        if max_price and max_price > 0 and price is not None:
            budget_score = max(0.0, 1.0 - (price / max_price) * 0.25)
        elif price is None:
            budget_score = 0.45
        else:
            budget_score = 0.75
        return rating_score * 0.8 + budget_score * 0.2

    return sorted(products, key=score, reverse=True)
