import base64
from datetime import datetime
import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from pathlib import Path
from pydantic import BaseModel
from starlette.responses import JSONResponse
from django.db import transaction

from users.endpoints import get_current_user
from .models import Product
from .crud import (
    add_to_cart, create_checkout_session, create_product, get_categories,
    get_or_create_cart, get_product, get_products, get_products_by_category,
    remove_from_cart, update_product, delete_product
)

router = APIRouter()

# Helper function to encode image as base64
def encode_image_to_base64(image_field) -> Optional[str]:
    if image_field and os.path.exists(image_field.path):
        try:
            with open(image_field.path, "rb") as image_file:
                base64_string = base64.b64encode(image_file.read()).decode("utf-8")
                return f"data:image/jpeg;base64,{base64_string}"
        except Exception as e:
            print(f"Error encoding image {image_field.path}: {e}")
            return None
    else:
        print(f"Image not found or missing: {image_field.path if image_field else 'None'}")
        return None

# Pydantic Models
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

class ProductImageResponse(BaseModel):
    id: int
    image: Optional[str] = None  # Base64-encoded image
    date: datetime

    class Config:
        orm_mode = True

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
    image: Optional[str] = None  # Base64-encoded main image
    additional_images: List[ProductImageResponse] = []  # Base64-encoded additional images

    class Config:
        orm_mode = True

class CategoryBase(BaseModel):
    title: str
    image: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(BaseModel):
    id: int
    title: str
    image: Optional[str] = None  # Base64-encoded image

    class Config:
        orm_mode = True

class CartItemBase(BaseModel):
    product_id: int
    quantity: int = 1
    size: str = 'M'

class CartResponse(BaseModel):
    id: int
    items: List[CartItemBase]
    total: float

    class Config:
        orm_mode = True

class CheckoutResponse(BaseModel):
    id: int
    status: str

    class Config:
        orm_mode = True

# ✅ List Products
@router.get("/products/", response_model=List[ProductResponse])
def list_products():
    products = get_products()
    product_responses = []
    for product in products:
        image_base64 = encode_image_to_base64(product.image)
        additional_images = [
            ProductImageResponse(
                id=img.id,
                image=encode_image_to_base64(img.images),
                date=img.date
            )
            for img in product.p_images.all()
        ]
        product_responses.append(
            ProductResponse(
                id=product.id,
                title=product.title,
                price=float(product.price),
                old_price=float(product.old_price),
                category_id=product.category_id,
                description=product.description,
                specifications=product.specifications,
                type=product.type,
                stock_count=product.stock_count,
                life=product.life,
                image=image_base64,
                additional_images=additional_images
            )
        )
    return product_responses

# ✅ Get a Product
@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product_detail(product_id: int):
    product = get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    image_base64 = encode_image_to_base64(product.image)
    additional_images = [
        ProductImageResponse(
            id=img.id,
            image=encode_image_to_base64(img.images),
            date=img.date
        )
        for img in product.p_images.all()
    ]
    
    return ProductResponse(
        id=product.id,
        title=product.title,
        price=float(product.price),
        old_price=float(product.old_price),
        category_id=product.category_id,
        description=product.description,
        specifications=product.specifications,
        type=product.type,
        stock_count=product.stock_count,
        life=product.life,
        image=image_base64,
        additional_images=additional_images
    )

# ✅ Create a Product
@router.post("/products/", status_code=201)
def create_product_endpoint(product_data: ProductCreate):
    with transaction.atomic():
        product = create_product(**product_data.dict())
    return JSONResponse(content=ProductResponse.from_orm(product).dict(), status_code=201)

# ✅ Update a Product
@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product_endpoint(product_id: int, product_data: ProductUpdate):
    with transaction.atomic():
        product = update_product(product_id, **product_data.dict(exclude_unset=True))
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    image_base64 = encode_image_to_base64(product.image)
    additional_images = [
        ProductImageResponse(
            id=img.id,
            image=encode_image_to_base64(img.images),
            date=img.date
        )
        for img in product.p_images.all()
    ]
    
    return ProductResponse(
        id=product.id,
        title=product.title,
        price=float(product.price),
        old_price=float(product.old_price),
        category_id=product.category_id,
        description=product.description,
        specifications=product.specifications,
        type=product.type,
        stock_count=product.stock_count,
        life=product.life,
        image=image_base64,
        additional_images=additional_images
    )

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
def list_categories(request: Request):
    categories = get_categories()
    category_responses = []

    for category in categories:
        image_base64 = encode_image_to_base64(category.image)
        category_responses.append(
            CategoryResponse(
                id=category.id,
                title=category.title,
                image=image_base64
            )
        )
    return category_responses

# ✅ Get Products by Category
@router.get("/products/category/{category_id}/", response_model=List[ProductResponse])
def list_products_by_category(category_id: int):
    products = get_products_by_category(category_id)
    if not products:
        raise HTTPException(status_code=404, detail="No products found for this category")
    
    product_responses = []
    for product in products:
        image_base64 = encode_image_to_base64(product.image)
        additional_images = [
            ProductImageResponse(
                id=img.id,
                image=encode_image_to_base64(img.images),
                date=img.date
            )
            for img in product.p_images.all()
        ]
        product_responses.append(
            ProductResponse(
                id=product.id,
                title=product.title,
                price=float(product.price),
                old_price=float(product.old_price),
                category_id=product.category_id,
                description=product.description,
                specifications=product.specifications,
                type=product.type,
                stock_count=product.stock_count,
                life=product.life,
                image=image_base64,
                additional_images=additional_images
            )
        )
    return product_responses

# ✅ Get or Create Cart
@router.get("/cart/", response_model=CartResponse)
def get_cart(user=Depends(get_current_user)):
    cart = get_or_create_cart(user)
    items = cart.items.all()
    total = sum(item.product.price * item.quantity for item in items)
    return CartResponse(
        id=cart.id,
        items=[CartItemBase(product_id=item.product.id, quantity=item.quantity, size=item.size) for item in items],
        total=total
    )

# ✅ Add to Cart
@router.post("/cart/items/", response_model=CartResponse)
def add_item_to_cart(item_data: CartItemBase, user=Depends(get_current_user)):
    cart = get_or_create_cart(user)
    cart_item = add_to_cart(cart, item_data.product_id, item_data.quantity, item_data.size)
    items = cart.items.all()
    total = sum(item.product.price * item.quantity for item in items)
    return CartResponse(
        id=cart.id,
        items=[CartItemBase(product_id=item.product.id, quantity=item.quantity, size=item.size) for item in items],
        total=total
    )

# ✅ Remove from Cart
@router.delete("/cart/items/{cart_item_id}")
def remove_item_from_cart(cart_item_id: int, user=Depends(get_current_user)):
    cart = get_or_create_cart(user)
    if remove_from_cart(cart, cart_item_id):
        return JSONResponse(content={"message": "Item removed from cart"}, status_code=200)
    raise HTTPException(status_code=404, detail="Item not found in cart")

# ✅ Create Checkout Session
@router.post("/checkout/", response_model=CheckoutResponse)
def create_checkout(user=Depends(get_current_user)):
    cart = get_or_create_cart(user)
    checkout_session = create_checkout_session(cart)
    return CheckoutResponse(id=checkout_session.id, status=checkout_session.status)