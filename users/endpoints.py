# from typing import List
# import jwt
# from datetime import datetime as d, timezone, timedelta
# from fastapi import APIRouter, Request, Depends, HTTPException, Security
# from pydantic import BaseModel
# from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
# from django.contrib.auth import authenticate, login, logout
# from starlette.responses import JSONResponse
# from django.contrib.auth.models import User
# from django.contrib.auth import get_user_model

# from django.conf import settings

# from users.crud import create_payment_method, create_shipping_address, delete_payment_method, delete_shipping_address, get_payment_methods, get_shipping_addresses, update_payment_method, update_shipping_address
# from users.models import BlacklistedToken

# router = APIRouter()
# User = get_user_model()  # This ensures Django uses the correct user model

# security = HTTPBearer()


# SECRET_KEY = settings.SECRET_KEY
# ALGORITHM = "HS256"

# # Pydantic models for request validation
# class LoginRequest(BaseModel):
#     username: str
#     password: str

# class RegisterRequest(BaseModel):
#     username: str
#     email: str
#     password: str

# class ShippingAddressRequest(BaseModel):
#     full_name: str
#     address_line1: str
#     address_line2: str = None
#     city: str
#     state: str = None
#     postal_code: str
#     country: str
#     phone: str = None
#     is_default: bool = False

# class ShippingAddressResponse(BaseModel):
#     id: int
#     full_name: str
#     address_line1: str
#     address_line2: str = None
#     city: str
#     state: str = None
#     postal_code: str
#     country: str
#     phone: str = None
#     is_default: bool
#     created_at: d
#     updated_at: d

#     class Config:
#         orm_mode = True

# class PaymentMethodRequest(BaseModel):
#     method_type: str = 'mpesa'  # Default to Mpesa
#     phone_number: str = None  # Required for Mpesa
#     last_four: str = None  # Optional for cards
#     is_default: bool = False

# class PaymentMethodResponse(BaseModel):
#     id: int
#     method_type: str
#     phone_number: str = None
#     last_four: str = None
#     is_default: bool
#     created_at: d
#     updated_at: d

#     class Config:
#         orm_mode = True
    
# def create_jwt_token(user_id):
#     payload = {
#         "user_id": user_id,
#         "exp": d.now(tz=timezone.utc) + timedelta(minutes=30),
#         "iat": d.now(tz=timezone.utc),
#     }
#     token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
#     return token

# # ✅ User Registration
# @router.post("/users/register", status_code=201)
# def register_user(request_data: RegisterRequest):
#     """
#     Register a new user.
#     """
#     if User.objects.filter(username=request_data.username).exists():
#         raise HTTPException(status_code=400, detail="Username already taken")
    
#     user = User.objects.create_user(
#         username=request_data.username,
#         email=request_data.email,
#         password=request_data.password
#     )
#     return JSONResponse(content={"message": "User registered successfully"}, status_code=201)


# # ✅ User Login (Session Creation)
# @router.post("/users/login")
# def login_user(request: Request, request_data: LoginRequest):
#     """
#     Authenticate user and create a session.
#     """
#     user = authenticate(username=request_data.username, password=request_data.password)
#     if not user:
#         raise HTTPException(status_code=401, detail="Invalid username or password")
    
#     token = create_jwt_token(user.id)
#     return JSONResponse(content={"access_token": token, "token_type": "bearer"}, status_code=200)

# # user authentication middleware
# def get_current_user(token: HTTPAuthorizationCredentials = Security(security),
# ):
#     if not token:
#         raise HTTPException(status_code=403, detail="Token missing")
#     print(token)
    
#     credentials_exception = HTTPException(status_code=403, detail="Invalid token")

#     try:
#         payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
#         if BlacklistedToken.objects.filter(token=token.credentials).exists():
#             raise credentials_exception
#         user = User.objects.get(id=payload["user_id"])
#         return user
#     except (jwt.ExpiredSignatureError, jwt.DecodeError, User.DoesNotExist):
#         raise credentials_exception

# # log out users by blacklisting the tokens
# @router.post("/users/logout")
# def logout_user(request: Request, token: str = Depends(get_current_user)):
#     """
#     Blacklist the JWT token upon logout.
#     """
#     if not token:
#         raise HTTPException(status_code=403, detail="Token missing")

#     # Save the token to the blacklist
#     if not BlacklistedToken.objects.filter(token=token).exists():
#       BlacklistedToken.objects.create(token=token)

#     return JSONResponse(content={"message": "Logout successful. Token invalidated."}, status_code=200)


# # ✅ Check Session Status
# @router.get("/users/session")
# def check_session_status(request: Request):
#     """
#     Check if a user is authenticated (session exists).
#     """
#     if not request.user.is_authenticated:
#         raise HTTPException(status_code=401, detail="User not authenticated")
    
#     return JSONResponse(content={"message": "Session is active", "user": request.user.username}, status_code=200)

# @router.get("/users/me")
# def get_user_profile(user: User=Depends(get_current_user)):
#     return JSONResponse(content={"username": user.username, "email": user.email})

# # Shipping Addresses
# @router.post("/users/shipping-addresses/", response_model=ShippingAddressResponse)
# def create_user_shipping_address(request_data: ShippingAddressRequest, user=Depends(get_current_user)):
#     address = create_shipping_address(user, request_data.dict(exclude_unset=True))
#     return address

# @router.get("/users/shipping-addresses/", response_model=List[ShippingAddressResponse])
# def get_user_shipping_addresses(user=Depends(get_current_user)):
#     addresses = get_shipping_addresses(user)
#     return list(addresses)

# @router.put("/users/shipping-addresses/{address_id}", response_model=ShippingAddressResponse)
# def update_user_shipping_address(address_id: int, request_data: ShippingAddressRequest, user=Depends(get_current_user)):
#     address = update_shipping_address(address_id, user, request_data.dict(exclude_unset=True))
#     return address

# @router.delete("/users/shipping-addresses/{address_id}")
# def delete_user_shipping_address(address_id: int, user=Depends(get_current_user)):
#     if delete_shipping_address(address_id, user):
#         return JSONResponse(content={"message": "Shipping address deleted successfully"}, status_code=200)
#     raise HTTPException(status_code=404, detail="Shipping address not found")

# # Payment Methods
# @router.post("/users/payment-methods/", response_model=PaymentMethodResponse)
# def create_user_payment_method(request_data: PaymentMethodRequest, user=Depends(get_current_user)):
#     payment_method = create_payment_method(user, request_data.dict(exclude_unset=True))
#     return payment_method

# @router.get("/users/payment-methods/", response_model=List[PaymentMethodResponse])
# def get_user_payment_methods(user=Depends(get_current_user)):
#     methods = get_payment_methods(user)
#     return list(methods)

# @router.put("/users/payment-methods/{method_id}", response_model=PaymentMethodResponse)
# def update_user_payment_method(method_id: int, request_data: PaymentMethodRequest, user=Depends(get_current_user)):
#     method = update_payment_method(method_id, user, request_data.dict(exclude_unset=True))
#     return method

# @router.delete("/users/payment-methods/{method_id}")
# def delete_user_payment_method(method_id: int, user=Depends(get_current_user)):
#     if delete_payment_method(method_id, user):
#         return JSONResponse(content={"message": "Payment method deleted successfully"}, status_code=200)
#     raise HTTPException(status_code=404, detail="Payment method not found")