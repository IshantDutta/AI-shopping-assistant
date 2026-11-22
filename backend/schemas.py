from typing import Optional
from urllib.parse import urlparse

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


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


class ChatRequest(BaseModel):
    message: str = Field(min_length=2, max_length=1000)
    max_price: Optional[float] = Field(default=None, ge=0)
    category: Optional[str] = Field(default=None, max_length=120)
    use_live_search: bool = True

    @field_validator("category")
    @classmethod
    def clean_category(cls, value):
        return value.strip() if value else value


class CompareProduct(BaseModel):
    """A product snapshot sent by the frontend for comparison."""
    id: Optional[int] = None
    name: str = Field(min_length=1, max_length=250)
    brand: str = Field(default="", max_length=160)
    category: str = Field(default="Other", max_length=120)
    price: Optional[float] = Field(default=None, ge=0)
    price_label: Optional[str] = Field(default=None, max_length=80)
    rating: Optional[float] = Field(default=None, ge=0, le=5)
    description: Optional[str] = Field(default=None, max_length=3000)
    image_url: Optional[str] = Field(default=None, max_length=2000)
    product_url: Optional[str] = Field(default=None, max_length=2000)
    source: str = Field(default="live", max_length=40)

    @field_validator("product_url", "image_url")
    @classmethod
    def validate_optional_url(cls, value):
        if not value:
            return value
        parsed = urlparse(value)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("URL must use http or https.")
        return value


class CompareRequest(BaseModel):
    # product_ids preserves compatibility with the original catalogue-only API.
    product_ids: Optional[list[int]] = Field(default=None, min_length=2, max_length=4)
    # products allows comparison of live SerpApi results, whose database id is null.
    products: Optional[list[CompareProduct]] = Field(default=None, min_length=2, max_length=4)

    @model_validator(mode="after")
    def require_one_comparison_input(self):
        if bool(self.product_ids) == bool(self.products):
            raise ValueError("Provide either product_ids or products (2 to 4 items).")
        return self
