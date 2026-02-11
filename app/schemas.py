from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime
from typing import List, Optional

class ProductBase(BaseModel):
    name: str
    quantity: int = Field(..., ge=0)
    price: Decimal = Field(..., gt=0)

class ProductCreate(ProductBase):
    category_id: Optional[int] = None

class ProductResponse(ProductBase):
    id: int
    category_id: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: Decimal
    
    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: int
    client_id: int
    created_at: datetime
    items: List[OrderItemResponse]
    
    class Config:
        from_attributes = True

class ClientTotal(BaseModel):
    client_id: int
    client_name: str
    total_sum: Decimal

class CategoryChildCount(BaseModel):
    category_id: int
    category_name: str
    level: int
    child_count_first_level: int

class TopProduct(BaseModel):
    product_name: str
    category_level_1: str
    total_sold: int

class AddToOrderResponse(BaseModel):
    success: bool
    message: str
    order_id: int
    product_id: int
    quantity_added: int
    total_quantity: int
