import json

from database import SessionLocal, engine, Base
from models import Product


# Make sure the database table exists
Base.metadata.create_all(bind=engine)


def seed_products():
    db = SessionLocal()

    try:
        # Prevent duplicate products if the script is run again
        existing_products = db.query(Product).count()

        if existing_products > 0:
            print(f"Database already contains {existing_products} products.")
            return

        # Load products from JSON
        with open("../data/products.json", "r", encoding="utf-8") as file:
            products = json.load(file)

        # Add products to database
        for product_data in products:
            product = Product(
                name=product_data["name"],
                brand=product_data["brand"],
                category=product_data["category"],
                price=product_data["price"],
                rating=product_data["rating"],
                description=product_data["description"],
                image_url=product_data["image_url"],
                product_url=product_data["product_url"]
            )

            db.add(product)

        db.commit()

        print(f"Successfully added {len(products)} products!")

    except Exception as error:
        db.rollback()
        print("Error while adding products:")
        print(error)

    finally:
        db.close()


if __name__ == "__main__":
    seed_products()