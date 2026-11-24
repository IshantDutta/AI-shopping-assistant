from typing import Any


def _number(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        number = float(value)
        return number if number >= 0 else None
    except (TypeError, ValueError):
        return None


def _availability(product: dict) -> str:
    status = str(product.get("availability_status") or "unknown").lower()
    if status in {"in_stock", "out_of_stock", "unknown"}:
        return status

    # Legacy/local products may only have availability text in their description.
    text = " ".join([
        str(product.get("description") or ""),
        " ".join(map(str, product.get("availability_details") or [])),
    ]).lower()
    if any(term in text for term in (
        "out of stock", "currently unavailable", "unavailable online",
        "sold out", "not available",
    )):
        return "out_of_stock"
    if any(term in text for term in (
        "in stock", "available online", "available now", "ready to ship",
    )):
        return "in_stock"
    return "unknown"


def build_comparison(products: list[dict]) -> dict:
    """Score only confirmed in-stock products; keep other products visible."""
    normalized = []
    for original in products:
        product = dict(original)
        product["availability_status"] = _availability(product)
        normalized.append(product)

    eligible = [
        (index, product) for index, product in enumerate(normalized)
        if product["availability_status"] == "in_stock"
    ]

    prices = [_number(p.get("price")) for _, p in eligible]
    known_prices = [price for price in prices if price is not None]
    cheapest = min(known_prices) if known_prices else None

    score_rows = []
    for index, product in enumerate(normalized):
        rating = _number(product.get("rating"))
        price = _number(product.get("price"))
        status = product["availability_status"]

        if status != "in_stock":
            score_rows.append({
                "index": index,
                "score": None,
                "eligible": False,
                "reason": (
                    "Out of stock; excluded from winner selection."
                    if status == "out_of_stock"
                    else "Availability unconfirmed; excluded from winner selection."
                ),
            })
            continue

        components = []
        if rating is not None:
            components.append((0.60, min(rating, 5.0) / 5.0 * 100))
        if price is not None and cheapest is not None and price > 0:
            components.append((0.40, min(cheapest / price, 1.0) * 100))
        elif price == 0:
            components.append((0.40, 100.0))

        if not components:
            score = None
            reason = "Insufficient price and rating data."
        else:
            weight_total = sum(weight for weight, _ in components)
            score = round(sum(weight * value for weight, value in components) / weight_total, 1)
            reason = "Score uses available rating (60%) and relative affordability (40%); missing fields are reweighted."

        score_rows.append({
            "index": index,
            "score": score,
            "eligible": score is not None,
            "reason": reason,
        })

    winner = max(
        (row for row in score_rows if row["eligible"] and row["score"] is not None),
        key=lambda row: row["score"],
        default=None,
    )
    best_name = normalized[winner["index"]].get("name") if winner else None

    return {
        "products": normalized,
        "summary": {
            "best_value_name": best_name,
            "best_value_index": winner["index"] if winner else None,
            "scores": score_rows,
            "method": (
                "Only confirmed in-stock products can win. Scores use up to "
                "60% customer rating and 40% relative affordability; missing "
                "data is reweighted. Unknown availability is not assumed in stock."
            ),
            "notice": (
                "Availability is based on the seller information returned by the shopping provider "
                "and may change. Confirm stock, shipping and final price on the merchant website."
            ),
        },
    }
