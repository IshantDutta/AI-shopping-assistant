from services.product_service import rank_products


def recommend(products: list[dict], max_price: float | None = None, limit: int = 8):
    return rank_products(products, max_price=max_price)[:limit]
