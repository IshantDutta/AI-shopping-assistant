from sqlalchemy import Column, Integer, String, Float, Text
from database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(250), nullable=False, index=True)
    brand = Column(String(120), nullable=False, default="")
    category = Column(String(120), nullable=False, index=True)
    price = Column(Float, nullable=False)
    rating = Column(Float, nullable=True)
    description = Column(Text, nullable=True)
    image_url = Column(String(1000), nullable=True)
    product_url = Column(String(1000), nullable=True)
