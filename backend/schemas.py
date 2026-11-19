from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    name: str
    brand: str = ""
    category: str
    price: float
    rating: Optional[float] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    product_url: Optional[str] = None
    source: str = "catalog"


class ChatRequest(BaseModel):
    message: str = Field(min_length=2, max_length=1000)
    max_price: Optional[float] = Field(default=None, ge=0)
    category: Optional[str] = None
    use_live_search: bool = True


class CompareRequest(BaseModel):
    product_ids: list[int] = Field(min_length=2, max_length=4)
