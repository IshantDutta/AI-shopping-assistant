from sqlalchemy import Column, Integer, String, Float, Text
from database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    brand = Column(String, nullable=False)

    category = Column(String, nullable=False)

    price = Column(Float, nullable=False)
    rating = Column(Float, nullable=True)

    description = Column(Text, nullable=True)

    image_url = Column(String, nullable=True)
    product_url = Column(String, nullable=True)