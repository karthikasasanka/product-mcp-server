from pydantic import BaseModel, Field
from typing import Optional


class ProductIn(BaseModel):
    name: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)
    description: Optional[str] = None


class Product(ProductIn):
    id: int

    class Config:
        from_attributes = True


