from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from starlette.responses import JSONResponse
from django.db import transaction
from .models import Product  # Assuming Product is one of your models
from .crud import create_product, get_categories, get_product, get_products, get_products_by_category, update_product, delete_product

router = APIRouter()

class ProductBase(BaseModel):
    title: str
    price: float
    old_price: float
    category_id: int
    description: Optional[str] = None
    specifications: Optional[str] = None
    type: Optional[str] = None
    stock_count: Optional[str] = None
    life: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    title: Optional[str] = None
    price: Optional[float] = None
    old_price: Optional[float] = None
    category_id: Optional[int] = None
    description: Optional[str] = None
    specifications: Optional[str] = None
    type: Optional[str] = None
    stock_count: Optional[str] = None
    life: Optional[str] = None

class ProductResponse(BaseModel):
    id: int
    title: str
    price: float
    old_price: float
    category_id: int
    description: Optional[str] = None
    specifications: Optional[str] = None
    type: Optional[str] = None
    stock_count: Optional[str] = None
    life: Optional[str] = None

    class Config:
        orm_mode = True

class CategoryBase(BaseModel):
    title: str

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(BaseModel):
    id: int
    title: str

    class Config:
        orm_mode = True

# ✅ List Products
@router.get("/products/")
def list_products():
    products = get_products()
    return JSONResponse(content=[ProductResponse.from_orm(product).dict() for product in products], status_code=200)

# ✅ Get a Product
@router.get("/products/{product_id}")
def get_product_detail(product_id: int):
    product = get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return JSONResponse(content=ProductResponse.from_orm(product).dict(), status_code=200)

# ✅ Create a Product
@router.post("/products/", status_code=201)
def create_product_endpoint(product_data: ProductCreate):
    with transaction.atomic():
        product = create_product(**product_data.dict())
    return JSONResponse(content=ProductResponse.from_orm(product).dict(), status_code=201)

# ✅ Update a Product
@router.put("/products/{product_id}")
def update_product_endpoint(product_id: int, product_data: ProductUpdate):
    with transaction.atomic():
        product = update_product(product_id, **product_data.dict(exclude_unset=True))
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return JSONResponse(content=ProductResponse.from_orm(product).dict(), status_code=200)

# ✅ Delete a Product
@router.delete("/products/{product_id}")
def delete_product_endpoint(product_id: int):
    with transaction.atomic():
        deleted = delete_product(product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")
    return JSONResponse(content={"message": "Product deleted successfully"}, status_code=200)

# ✅ List Categories
@router.get("/categories/", response_model=List[CategoryResponse])
def list_categories():
    categories = get_categories()
    return [CategoryResponse.from_orm(category) for category in categories]

# ✅ Get Products by Category
@router.get("/products/category/{category_id}/", response_model=List[ProductResponse])
def list_products_by_category(category_id: int):
    products = get_products_by_category(category_id)
    if not products:
        raise HTTPException(status_code=404, detail="No products found for this category")
    return [ProductResponse.from_orm(product) for product in products]