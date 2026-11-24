from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    name: str
    brand: str = ""
    category: str
    price: Optional[float] = None
    rating: Optional[float] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    product_url: Optional[str] = None
    price_label: Optional[str] = None
    source: str = "catalog"
    availability_status: str = "unknown"
    availability_details: list[str] = Field(default_factory=list)


class CompareProduct(BaseModel):
    id: Optional[int] = None
    name: str = Field(min_length=1, max_length=300)
    brand: str = ""
    category: str = "Uncategorized"
    price: Optional[float] = Field(default=None, ge=0)
    price_label: Optional[str] = None
    rating: Optional[float] = Field(default=None, ge=0, le=5)
    description: Optional[str] = None
    image_url: Optional[str] = None
    product_url: Optional[str] = None
    source: str = "catalog"
    availability_status: str = "unknown"
    availability_details: list[str] = Field(default_factory=list)


class ChatRequest(BaseModel):
    message: str = Field(min_length=2, max_length=1000)
    max_price: Optional[float] = Field(default=None, ge=0)
    category: Optional[str] = Field(default=None, max_length=120)
    use_live_search: bool = True

    @field_validator("category")
    @classmethod
    def clean_category(cls, value):
        return value.strip() if value else value


class CompareRequest(BaseModel):
    products: list[CompareProduct] = Field(min_length=2, max_length=4)
    product_ids: Optional[list[int]] = None
