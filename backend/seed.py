import json
from pathlib import Path

from database import Base, SessionLocal, engine
from models import Product

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "data" / "products.json"


def seed_products():
    Base.metadata.create_all(bind=engine)
    with DATA_FILE.open("r", encoding="utf-8") as file:
        items = json.load(file)

    db = SessionLocal()
    added = 0
    updated = 0
    try:
        for item in items:
            existing = db.query(Product).filter(
                Product.name == item["name"],
                Product.brand == item.get("brand", ""),
            ).first()

            if existing:
                for key in (
                    "category", "price", "rating", "description",
                    "image_url", "product_url",
                ):
                    setattr(existing, key, item.get(key))
                updated += 1
            else:
                db.add(Product(**item))
                added += 1

        db.commit()
        print(f"Seed complete: {added} added, {updated} updated.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_products()
