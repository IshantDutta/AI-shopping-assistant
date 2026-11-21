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
    product_ids: list[int] = Field(min_length=2, max_length=4)
