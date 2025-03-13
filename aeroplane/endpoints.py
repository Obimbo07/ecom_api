# import base64
# from datetime import datetime
# import os
# from typing import List, Optional
# from fastapi import APIRouter, Depends, HTTPException, Request
# from pathlib import Path
# from pydantic import BaseModel
# from starlette.responses import JSONResponse
# from django.db import transaction

# from users.endpoints import get_current_user
# from users.models import PaymentMethod, ShippingAddress
# from .models import RATING, Cart, CheckoutSession, Order, OrderItem, Product
# from .crud import (
#     add_to_cart, create_checkout_session, create_pro_review, create_product, delete_product_review, get_categories,
#     get_or_create_cart, get_product, get_product_reviews, get_products, get_products_by_category, initiate_mpesa_stk_push, process_mpesa_callback, process_mpesa_query,
#     remove_from_cart, update_cart_it, update_product, delete_product, update_product_review
# )

# router = APIRouter()

# # Helper function to encode image as base64
# def encode_image_to_base64(image_field) -> Optional[str]:
#     if image_field and os.path.exists(image_field.path):
#         try:
#             with open(image_field.path, "rb") as image_file:
#                 base64_string = base64.b64encode(image_file.read()).decode("utf-8")
#                 return f"data:image/jpeg;base64,{base64_string}"
#         except Exception as e:
#             print(f"Error encoding image {image_field.path}: {e}")
#             return None
#     else:
#         print(f"Image not found or missing: {image_field.path if image_field else 'None'}")
#         return None

# # Pydantic Models
# class ProductBase(BaseModel):
#     title: str
#     price: float
#     old_price: float
#     category_id: int
#     description: Optional[str] = None
#     specifications: Optional[str] = None
#     type: Optional[str] = None
#     stock_count: Optional[str] = None
#     life: Optional[str] = None

# class ProductCreate(ProductBase):
#     pass

# class ProductUpdate(BaseModel):
#     title: Optional[str] = None
#     price: Optional[float] = None
#     old_price: Optional[float] = None
#     category_id: Optional[int] = None
#     description: Optional[str] = None
#     specifications: Optional[str] = None
#     type: Optional[str] = None
#     stock_count: Optional[str] = None
#     life: Optional[str] = None

# class ProductImageResponse(BaseModel):
#     id: int
#     image: Optional[str] = None  # Base64-encoded image
#     date: datetime

#     class Config:
#         orm_mode = True

# class ProductResponse(BaseModel):
#     id: int
#     title: str
#     price: float
#     old_price: float
#     category_id: int
#     description: Optional[str] = None
#     specifications: Optional[str] = None
#     type: Optional[str] = None
#     stock_count: Optional[str] = None
#     life: Optional[str] = None
#     image: Optional[str] = None  # Base64-encoded main image
#     additional_images: List[ProductImageResponse] = []  # Base64-encoded additional images

#     class Config:
#         orm_mode = True

# class CategoryBase(BaseModel):
#     title: str
#     image: Optional[str] = None

# class CategoryCreate(CategoryBase):
#     pass

# class CategoryResponse(BaseModel):
#     id: int
#     title: str
#     image: Optional[str] = None  # Base64-encoded image

#     class Config:
#         orm_mode = True

# class CartItemBase(BaseModel):
#     id: Optional[int] = None
#     product_id: int
#     quantity: int = 1
#     size: str = 'M'

# class CartResponse(BaseModel):
#     id: int
#     items: List[CartItemBase]
#     total: float

#     class Config:
#         orm_mode = True

# class CheckoutResponse(BaseModel):
#     id: int
#     status: str

#     class Config:
#         orm_mode = True

# class CartItemUpdate(BaseModel):
#     quantity: Optional[int] = None
#     size: Optional[str] = None

# class OrderCreateResponse(BaseModel):
#     id: int
#     total_amount: float
#     status: str
#     payment_status: str

#     class Config:
#         orm_mode = True

# class OrderItemResponse(BaseModel):
#     product_title: str
#     quantity: int
#     price: float
#     size: Optional[str] = None  # Some products may not have sizes

#     class Config:
#         orm_mode = True

# class OrderResponse(BaseModel):
#     id: int
#     total_amount: float
#     status: str
#     payment_status: str
#     created_at: datetime
#     items: List[OrderItemResponse] = []

#     class Config:
#         orm_mode = True


# class ProductReviewRequest(BaseModel):
#     rating: int
#     review_text: str = None

# class ProductReviewResponse(BaseModel):
#     id: int
#     user: str  # Username
#     product: int  # Product ID
#     rating: int
#     review_text: str = None
#     created_at: datetime
#     updated_at: datetime
#     is_approved: bool

#     class Config:
#         orm_mode = True

# # ✅ List Products
# @router.get("/products/", response_model=List[ProductResponse])
# def list_products():
#     products = get_products()
#     product_responses = []
#     for product in products:
#         image_base64 = encode_image_to_base64(product.image)
#         additional_images = [
#             ProductImageResponse(
#                 id=img.id,
#                 image=encode_image_to_base64(img.images),
#                 date=img.date
#             )
#             for img in product.p_images.all()
#         ]
#         product_responses.append(
#             ProductResponse(
#                 id=product.id,
#                 title=product.title,
#                 price=float(product.price),
#                 old_price=float(product.old_price),
#                 category_id=product.category_id,
#                 description=product.description,
#                 specifications=product.specifications,
#                 type=product.type,
#                 stock_count=product.stock_count,
#                 life=product.life,
#                 image=image_base64,
#                 additional_images=additional_images
#             )
#         )
#     return product_responses

# # ✅ Get a Product
# @router.get("/products/{product_id}", response_model=ProductResponse)
# def get_product_detail(product_id: int):
#     product = get_product(product_id)
#     if not product:
#         raise HTTPException(status_code=404, detail="Product not found")
    
#     image_base64 = encode_image_to_base64(product.image)
#     additional_images = [
#         ProductImageResponse(
#             id=img.id,
#             image=encode_image_to_base64(img.images),
#             date=img.date
#         )
#         for img in product.p_images.all()
#     ]
    
#     return ProductResponse(
#         id=product.id,
#         title=product.title,
#         price=float(product.price),
#         old_price=float(product.old_price),
#         category_id=product.category_id,
#         description=product.description,
#         specifications=product.specifications,
#         type=product.type,
#         stock_count=product.stock_count,
#         life=product.life,
#         image=image_base64,
#         additional_images=additional_images
#     )

# # ✅ Create a Product
# @router.post("/products/", status_code=201)
# def create_product_endpoint(product_data: ProductCreate):
#     with transaction.atomic():
#         product = create_product(**product_data.dict())
#     return JSONResponse(content=ProductResponse.from_orm(product).dict(), status_code=201)

# # ✅ Update a Product
# @router.put("/products/{product_id}", response_model=ProductResponse)
# def update_product_endpoint(product_id: int, product_data: ProductUpdate):
#     with transaction.atomic():
#         product = update_product(product_id, **product_data.dict(exclude_unset=True))
#     if not product:
#         raise HTTPException(status_code=404, detail="Product not found")
    
#     image_base64 = encode_image_to_base64(product.image)
#     additional_images = [
#         ProductImageResponse(
#             id=img.id,
#             image=encode_image_to_base64(img.images),
#             date=img.date
#         )
#         for img in product.p_images.all()
#     ]
    
#     return ProductResponse(
#         id=product.id,
#         title=product.title,
#         price=float(product.price),
#         old_price=float(product.old_price),
#         category_id=product.category_id,
#         description=product.description,
#         specifications=product.specifications,
#         type=product.type,
#         stock_count=product.stock_count,
#         life=product.life,
#         image=image_base64,
#         additional_images=additional_images
#     )

# # ✅ Delete a Product
# @router.delete("/products/{product_id}")
# def delete_product_endpoint(product_id: int):
#     with transaction.atomic():
#         deleted = delete_product(product_id)
#     if not deleted:
#         raise HTTPException(status_code=404, detail="Product not found")
#     return JSONResponse(content={"message": "Product deleted successfully"}, status_code=200)

# # ✅ List Categories
# @router.get("/categories/", response_model=List[CategoryResponse])
# def list_categories(request: Request):
#     categories = get_categories()
#     category_responses = []

#     for category in categories:
#         image_base64 = encode_image_to_base64(category.image)
#         category_responses.append(
#             CategoryResponse(
#                 id=category.id,
#                 title=category.title,
#                 image=image_base64
#             )
#         )
#     return category_responses

# # ✅ Get Products by Category
# @router.get("/products/category/{category_id}/", response_model=List[ProductResponse])
# def list_products_by_category(category_id: int):
#     products = get_products_by_category(category_id)
#     if not products:
#         raise HTTPException(status_code=404, detail="No products found for this category")
    
#     product_responses = []
#     for product in products:
#         image_base64 = encode_image_to_base64(product.image)
#         additional_images = [
#             ProductImageResponse(
#                 id=img.id,
#                 image=encode_image_to_base64(img.images),
#                 date=img.date
#             )
#             for img in product.p_images.all()
#         ]
#         product_responses.append(
#             ProductResponse(
#                 id=product.id,
#                 title=product.title,
#                 price=float(product.price),
#                 old_price=float(product.old_price),
#                 category_id=product.category_id,
#                 description=product.description,
#                 specifications=product.specifications,
#                 type=product.type,
#                 stock_count=product.stock_count,
#                 life=product.life,
#                 image=image_base64,
#                 additional_images=additional_images
#             )
#         )
#     return product_responses

# # ✅ Get or Create Cart
# @router.get("/cart/", response_model=CartResponse)
# def get_cart(user=Depends(get_current_user)):
#     cart = get_or_create_cart(user)
#     items = cart.items.all()
#     total = sum(item.product.price * item.quantity for item in items)
#     return CartResponse(
#         id=cart.id,
#         items=[CartItemBase(id=item.id, product_id=item.product.id, quantity=item.quantity, size=item.size) for item in items],
#         total=total
#     )

# # ✅ Add to Cart
# @router.post("/cart/items/", response_model=CartResponse)
# def add_item_to_cart(item_data: CartItemBase, user=Depends(get_current_user)):
#     print(f"Received item_data: {item_data}")  # Debug: Log the received data 
#     cart = get_or_create_cart(user)
#     cart_item = add_to_cart(cart, item_data.product_id, item_data.quantity, item_data.size)
#     items = cart.items.all()
#     total = sum(item.product.price * item.quantity for item in items)
#     return CartResponse(
#         id=cart.id,
#         items=[CartItemBase(id= item.id, product_id=item.product.id, quantity=item.quantity, size=item.size) for item in items],
#         total=total
#     )

# # ✅ Update Cart Item
# @router.put("/cart/items/{cart_item_id}", response_model=CartResponse)
# def update_cart_item(cart_item_id: int, item_data: CartItemUpdate, user=Depends(get_current_user)):
#     """
#     Update the quantity and/or size of a specific cart item.
#     """
#     cart = get_or_create_cart(user)
#     try:
#         # Ensure we’re passing only the expected 
#         print('bafore')
#         updated_cart = update_cart_it(cart, cart_item_id, quantity=item_data.quantity, size=item_data.size)
#         print('after')
#         items = updated_cart.items.all()
#         total = sum(item.product.price * item.quantity for item in items)
#         return CartResponse(
#             id=updated_cart.id,
#             items=[CartItemBase(id=item.id, product_id=item.product.id, quantity=item.quantity, size=item.size) for item in items],
#             total=total
#         )
#     except ValueError as e:
#         raise HTTPException(status_code=404, detail=str(e))
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
# # ✅ Remove from Cart
# @router.delete("/cart/items/{cart_item_id}")
# def remove_item_from_cart(cart_item_id: int, user=Depends(get_current_user)):
#     cart = get_or_create_cart(user)
#     if remove_from_cart(cart, cart_item_id):
#         return JSONResponse(content={"message": "Item removed from cart"}, status_code=200)
#     raise HTTPException(status_code=404, detail="Item not found in cart")

# # ✅ Create Checkout Session
# @router.post("/checkout/", response_model=CheckoutResponse)
# def create_checkout(user=Depends(get_current_user)):
#     cart = get_or_create_cart(user)
#     checkout_session = create_checkout_session(cart)
#     return CheckoutResponse(id=checkout_session.id, status=checkout_session.status)


# @router.post("/orders/", response_model=OrderCreateResponse)
# def create_order(user=Depends(get_current_user)):
#     cart = Cart.objects.filter(user=user, is_active=True).first()
#     if not cart or not cart.items.exists():
#         raise HTTPException(status_code=400, detail="Cart is empty or does not exist")

#     with transaction.atomic():
#         total_amount = sum(item.product.price * item.quantity for item in cart.items.all())
#         order = Order.objects.create(
#             user=user,
#             total_amount=total_amount,
#             status="pending",
#             payment_status="unpaid"
#         )

#         for item in cart.items.all():
#             OrderItem.objects.create(
#                 order=order,
#                 product=item.product,
#                 quantity=item.quantity,
#                 price=item.product.price,
#                 size=item.size
#             )

#         cart.is_active = False
#         cart.save()

#         return OrderCreateResponse(
#             id=order.id,
#             total_amount=float(order.total_amount),
#             status=order.status,
#             payment_status=order.payment_status
#         )

# @router.get("/orders/{order_id}/items/", response_model=List[OrderItemResponse])
# def get_order_items(order_id: int, user=Depends(get_current_user)):
#     """
#     Fetch all items in an order.
#     """
#     try:
#         order = Order.objects.get(id=order_id, user=user)

#     except Order.DoesNotExist:
#         raise HTTPException(status_code=404, detail="Order not found")

#     order_items = order.items.all()  # Fetch related OrderItems
#     return [
#         OrderItemResponse(
#             product_title=item.product.title,
#             quantity=item.quantity,
#             price=float(item.price),  # Convert Decimal to float
#             size=item.size
#         )
#         for item in order_items
#     ]

# @router.get("/user/orders/", response_model=List[OrderResponse])
# def get_user_orders(user=Depends(get_current_user)):
#     """
#     Fetch all orders for the authenticated user.
#     """
#     try:
#         # Fetch all orders for the user
#         orders = Order.objects.filter(user=user).order_by('-created_at')
        
#         if not orders.exists():
#             return []  # Return empty list if no orders found

#         order_responses = []
#         for order in orders:
#             order_items = order.items.all()
#             order_responses.append(
#                 OrderResponse(
#                     id=order.id,
#                     total_amount=float(order.total_amount),
#                     status=order.status,
#                     payment_status=order.payment_status,
#                     created_at=order.created_at,
#                     items=[
#                         OrderItemResponse(
#                             product_title=item.product.title,
#                             quantity=item.quantity,
#                             price=float(item.price),
#                             size=item.size
#                         )
#                         for item in order_items
#                     ]
#                 )
#             )
#         return order_responses

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    

# # Product Reviews
# @router.post("/products/{product_id}/reviews/", response_model=ProductReviewResponse)
# def create_product_review(product_id: int, review_data: ProductReviewRequest, user=Depends(get_current_user)):
#     """
#     Create a review for a specific product by the authenticated user.
#     """
#     print(review_data, 'reviews')
#     print(product_id, 'reviews')
#     # Ensure review_data is a ProductReviewRequest instance
#     if not isinstance(review_data, ProductReviewRequest):
#         raise HTTPException(status_code=400, detail="Invalid request body: expected review data with rating")

#     # Validate rating against RATING choices
#     if review_data.rating not in [choice[0] for choice in RATING]:
#         raise HTTPException(status_code=400, detail="Invalid rating value")
    
#     # Convert Pydantic model to dictionary and pass it to the CRUD function
#     data = review_data.dict(exclude_unset=True)
#     review = create_pro_review(user, product_id, data)
#     return review

# @router.get("/products/{product_id}/reviews/", response_model=List[ProductReviewResponse])
# def list_product_reviews(product_id: int, user=Depends(get_current_user)):
#     reviews = get_product_reviews(product_id=product_id)
#     return reviews

# @router.get("/users/reviews/", response_model=List[ProductReviewResponse])
# def list_user_reviews(user=Depends(get_current_user)):
#     reviews = get_product_reviews(user=user)
#     return reviews

# @router.put("/reviews/{review_id}", response_model=ProductReviewResponse)
# def update_product_review_endpoint(review_id: int, review_data: ProductReviewRequest, user=Depends(get_current_user)):
#     data = review_data.dict(exclude_unset=True)
#     if data.get('rating') and data['rating'] not in [choice[0] for choice in RATING]:
#         raise HTTPException(status_code=400, detail="Invalid rating value")
#     review = update_product_review(review_id, user, data)
#     return review

# @router.delete("/reviews/{review_id}")
# def delete_product_review_endpoint(review_id: int, user=Depends(get_current_user)):
#     if delete_product_review(review_id, user):
#         return JSONResponse(content={"message": "Review deleted successfully"}, status_code=200)
#     raise HTTPException(status_code=404, detail="Review not found or unauthorized")


# class CheckoutSessionRequest(BaseModel):
#     order_id: int
#     shipping_address_id: int
#     payment_method_id: int
#     phone_number: str  # M-Pesa phone number (e.g., 254708374149)

# class CheckoutSessionResponse(BaseModel):
#     checkout_request_id: str
#     merchant_request_id: str
#     response_code: str
#     response_description: str
#     customer_message: str

# @router.post("/checkout-session/", response_model=CheckoutSessionResponse)
# def create_checkout_session(request: CheckoutSessionRequest, user=Depends(get_current_user)):
#     try:
#         print(request.order_id)
#         order = Order.objects.get(id=request.order_id, user=user)
#         print(order)

#         if order.payment_status != "unpaid":
#             raise HTTPException(status_code=400, detail="Order already processed")

#         shipping_address = ShippingAddress.objects.get(id=request.shipping_address_id, user=user)
#         payment_method = PaymentMethod.objects.get(id=request.payment_method_id, user=user)
#         print(payment_method, shipping_address)
#         # Calculate order total (ensure it matches your items)
#         order_total = sum(item.price * item.quantity for item in order.items.all())
        
#         # Use the phone number from payment_method or request
#         phone_number = request.phone_number or payment_method.phone_number
#         print(phone_number, "number")
#         if not phone_number or not phone_number.startswith('254'):
#             raise HTTPException(status_code=400, detail="Invalid M-Pesa phone number")
#         print(order, phone_number, order_total, 'sjwjqsdn')
#         # Initiate M-Pesa STK Push
#         callback_url = f"https://admin.mohacollection.co.ke/mpesa-callback"
#         mpesa_response = initiate_mpesa_stk_push(order, phone_number, order_total, callback_url)
#         print(mpesa_response, 'stk push response')

#         transformed_response = CheckoutSessionResponse(
#             checkout_request_id=mpesa_response['CheckoutRequestID'],
#             merchant_request_id=mpesa_response['MerchantRequestID'],
#             response_code=mpesa_response['ResponseCode'],
#             response_description=mpesa_response['ResponseDescription'],
#             customer_message=mpesa_response['CustomerMessage']
#         )

#         return transformed_response
#     except (Order.DoesNotExist, ShippingAddress.DoesNotExist, PaymentMethod.DoesNotExist):
#         raise HTTPException(status_code=404, detail="Order, shipping address, or payment method not found")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    
# @router.post("/mpesa-callback/")
# async def mpesa_callback(request: Request):
#     try:
#         body = await request.json()
#         result = await process_mpesa_callback(body)
#         print(result, 'result')
#         if result['status'] == 'error':
#             raise HTTPException(status_code=500, detail=result['message'])
#         return JSONResponse(content={'status': 'success', 'message': result['message']})
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# class MpesaQueryRequest(BaseModel):
#     checkout_request_id: str

# class MpesaQueryResponse(BaseModel):
#    ResponseCode: str    
#    ResponseDescription: str
#    MerchantRequestID:  str
#    CheckoutRequestID: str
#    ResultCode: str
#    ResultDesc: str

# @router.post("/query-mpesa/", response_model=MpesaQueryResponse)
# async def query_mpesa(request: MpesaQueryRequest, user=Depends(get_current_user)):
#     try:
#         # The request body is already parsed into the MpesaQueryRequest model
#         # No need to call request.json()
#         body = request.dict()  # Convert Pydantic model to dictionary for processing
#         print(body, 'body')

#         # Assuming process_mpesa_query is an async function
#         result =  process_mpesa_query(body)
#         print(result, 'result')

#         # Check for error in the result
#         if result.get('status') == 'error':
#             raise HTTPException(status_code=500, detail=result.get('message', 'Unknown error'))

#         # Return success response
#         return JSONResponse(content={'status': 'success', 'message': result.get('message', 'Query successful')})

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))    