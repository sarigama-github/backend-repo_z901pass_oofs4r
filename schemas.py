"""
Database Schemas for Vic Signature

Define MongoDB collection schemas here using Pydantic models.
Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name.
"""

from pydantic import BaseModel, Field
from typing import Optional, List

class Category(BaseModel):
    name: str = Field(..., description="Category name")
    slug: str = Field(..., description="URL-friendly slug")
    description: Optional[str] = Field(None, description="Short description of the category")

class Product(BaseModel):
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Category slug")
    images: List[str] = Field(default_factory=list, description="Image URLs")
    in_stock: bool = Field(True, description="Whether product is in stock")
    tags: List[str] = Field(default_factory=list, description="Product tags")

class CartItem(BaseModel):
    product_id: str = Field(..., description="Referenced product _id as string")
    title: str = Field(..., description="Snapshot of product title at time of order")
    quantity: int = Field(..., ge=1, description="Quantity")
    price: float = Field(..., ge=0, description="Unit price at time of order")
    image: Optional[str] = Field(None, description="Primary image URL")

class Customer(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None

class Order(BaseModel):
    items: List[CartItem]
    customer: Customer
    subtotal: float = Field(..., ge=0)
    shipping: float = Field(0, ge=0)
    total: float = Field(..., ge=0)
    status: str = Field("pending", description="pending, paid, fulfilled, cancelled")
