import base64
from datetime import datetime
import os
from django.utils import timezone
from typing import List, Optional
from django.db import transaction
from fastapi import HTTPException
import requests
from .models import Cart, CartItem, Category, CheckoutSession, Order, Product, ProductReview  # Assuming Product is one of your models


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


def create_product(**kwargs):
    """
    Creates a new product in the database.
    
    :param kwargs: Keyword arguments representing Product model fields
    :return: The created Product instance
    """
    with transaction.atomic():
        product = Product.objects.create(**kwargs)
    return product

def get_product(product_id: int):
    """
    Retrieves a product from the database by its ID.
    
    :param product_id: The ID of the product to retrieve
    :return: The Product instance or None if not found
    """
    try:
        return Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return None

def get_products() -> List[Product]:
    """
    Retrieves all products from the database.
    
    :return: A list of all Product instances
    """
    return list(Product.objects.all())

def update_product(product_id: int, **kwargs):
    """
    Updates an existing product in the database.
    
    :param product_id: The ID of the product to update
    :param kwargs: Keyword arguments representing fields to update
    :return: The updated Product instance or None if not found
    """
    with transaction.atomic():
        try:
            product = Product.objects.get(id=product_id)
            for key, value in kwargs.items():
                setattr(product, key, value)
            product.save()
            return product
        except Product.DoesNotExist:
            return None

def delete_product(product_id: int) -> bool:
    """
    Deletes a product from the database.
    
    :param product_id: The ID of the product to delete
    :return: True if the product was deleted, False otherwise
    """
    with transaction.atomic():
        try:
            product = Product.objects.get(id=product_id)
            product.delete()
            return True
        except Product.DoesNotExist:
            return False
    
def get_categories() -> List[Category]:
    return list(Category.objects.all())

def get_products_by_category(category_id: int) -> List[Product]:
    try:
        return list(Product.objects.filter(category_id=category_id))
    except Product.DoesNotExist:
        return []
    
def create_cart(user=None) -> Cart:
    with transaction.atomic():
        cart = Cart.objects.create(user=user)
    return cart

def get_or_create_cart(user=None) -> Cart:
    if user:
        cart = Cart.objects.filter(user=user, is_active=True).first()
        if not cart:
            cart = create_cart(user)
    else:
        cart = Cart.objects.filter(user__isnull=True, is_active=True).first()
        if not cart:
            cart = create_cart()
    return cart

def add_to_cart(cart: Cart, product_id: int, quantity: int = 1, size: str = 'M') -> CartItem:
    print(cart, 'cart in Data')
    print(product_id, 'product_id in Data')
    print(quantity, 'quantity in Data')
    print(size, 'size in Data')
    with transaction.atomic():
        product = Product.objects.get(id=product_id)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            size=size,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        return 
    
def update_cart_it(cart: Cart, cart_item_id: int, quantity: int = None, size: str = None) -> Cart:
    print(cart, 'cart in Data')

    """
    Update the quantity and/or size of a specific cart item.
    
    Args:
        cart: The user's cart instance.
        cart_item_id: The ID of the cart item to update.
        quantity: Optional new quantity (if provided, must be > 0).
        size: Optional new size (if provided, must be a valid size, e.g., 'XS', 'S', 'M', 'L', 'XL').
    
    Raises:
        ValueError: If the cart item is not found or if the update is invalid.
    """
    print(f"Received args: cart={cart}, cart_item_id={cart_item_id}, quantity={quantity}, size={size}")
    try:
        cart_item = cart.items.get(id=cart_item_id)
        print(cart_item, 'cart Data')
        
    except CartItem.DoesNotExist:
        raise ValueError("Cart item not found")
    if quantity is not None:
      new_quantity = cart_item.quantity + quantity

      if new_quantity < 1:
        raise ValueError("Quantity must be greater than 0")
      cart_item.quantity = new_quantity
    if size is not None:
        # Validate size (you can customize this validation based on your needs)
        valid_sizes = ['XS', 'S', 'M', 'L', 'XL', 'string']            
        if size not in valid_sizes:
            raise ValueError("Invalid size provided")
        cart_item.size = size

    cart_item.save()
    return cart

def remove_from_cart(cart: Cart, cart_item_id: int) -> bool:
    with transaction.atomic():
        try:
            cart_item = CartItem.objects.get(id=cart_item_id, cart=cart)
            print(cart_item)
            cart_item.delete()
            return True
        except CartItem.DoesNotExist:
            return False

def create_checkout_session(cart: Cart) -> CheckoutSession:
    with transaction.atomic():

        checkout_session = CheckoutSession.objects.create(
            cart=cart,
            status='draft'
        )
        return checkout_session 
    

def create_pro_review(user, product_id, data):
    """
    Create a product review for a specific product by a user and return a response-compatible dict.
    """
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        raise ValueError("Product not found")
    
    if 'rating' not in data or not isinstance(data['rating'], int):
        raise ValueError("Rating is required and must be an integer")
    
    review = ProductReview.objects.create(user=user, product=product, **data)
    
    # Return a dict matching ProductReviewResponse
    return review

def get_product_reviews(product_id=None, user=None):
    """
    Retrieve product reviews, optionally filtered by product_id or user, returning a list of dicts.
    """
    queryset = ProductReview.objects.all()
    if product_id:
        queryset = queryset.filter(product_id=product_id)
    if user:
        queryset = queryset.filter(user=user)
    
    return queryset  # Convert QuerySet to list
    
def update_product_review(review_id, user, data):
    review = ProductReview.objects.filter(id=review_id, user=user).first()
    if not review:
        raise ValueError("Review not found or unauthorized")
    for key, value in data.items():
        setattr(review, key, value)
    review.save()
    return review

def delete_product_review(review_id, user):
    review = ProductReview.objects.filter(id=review_id, user=user).first()
    if not review:
        raise ValueError("Review not found or unauthorized")
    review.delete()
    return True


from django.conf import settings
from .models import MpesaTransaction

def generate_mpesa_access_token():
    """
    Generate an access token for M-Pesa API using Consumer Key and Secret.
    """
    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET
    credentials = f"{consumer_key}:{consumer_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode('utf-8')
    
    url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    headers = {
        'Authorization': f'Basic {encoded_credentials}',
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['access_token']

def generate_mpesa_password(business_shortcode, passkey, timestamp):
    """
    Generate the M-Pesa password (base64 encoded combination of Shortcode, Passkey, and Timestamp).
    """
    password = f"{business_shortcode}{passkey}{timestamp}"
    return base64.b64encode(password.encode()).decode('utf-8')

def initiate_mpesa_stk_push(order: Order, phone_number: str, amount: float, callback_url: str):
    """
    Initiate an M-Pesa STK Push request for a given order and create an MpesaTransaction record.
    """
    business_shortcode = settings.MPESA_BUSINESS_SHORTCODE
    passkey = settings.MPESA_PASSKEY
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    
    password = generate_mpesa_password(business_shortcode, passkey, timestamp)
    
    payload = {
        "BusinessShortCode": business_shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": phone_number,
        "PartyB": business_shortcode,
        "PhoneNumber": phone_number,
        "CallBackURL": callback_url,
        "AccountReference": f"Order_{order.id}",
        "TransactionDesc": f"Payment for Order {order.id}"
    }
    
    access_token = generate_mpesa_access_token()
    url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
    }
    
    response = requests.post(url, json=payload, headers=headers)
    response.text.encode('utf-8')
    print(response, "mpesa response")

    
    mpesa_response = response.json()
    print(mpesa_response, 'mpesa response')
    
    # Create or update MpesaTransaction
    checkout_session, _ = CheckoutSession.objects.get_or_create(order=order)
    mpesa_transaction, created = MpesaTransaction.objects.get_or_create(
        order=order,
        defaults={
            'checkout_session': checkout_session,
            'merchant_request_id': mpesa_response['MerchantRequestID'],
            'checkout_request_id': mpesa_response['CheckoutRequestID'],
            'result_desc': mpesa_response['ResponseDescription'],
            'result_code': mpesa_response['ResponseCode'],
            'phone_number': phone_number,
            'amount': amount,
            'status': 'pending',
        }
    )
    
    if not created:
        mpesa_transaction.merchant_request_id = mpesa_response['MerchantRequestID']
        mpesa_transaction.checkout_request_id = mpesa_response['CheckoutRequestID']
        mpesa_transaction.result_code = mpesa_response['ResponseCode']
        mpesa_transaction.result_desc = mpesa_response['ResponseDescription']
        mpesa_transaction.phone_number = phone_number
        mpesa_transaction.amount = amount
        mpesa_transaction.status = 'pending'
        mpesa_transaction.save()

     # Update the checkout_session's mpesa_receipt_number with the checkout_request_id
    
    return mpesa_response

from asgiref.sync import sync_to_async

@sync_to_async
def process_mpesa_callback(callback_data):
    """
    Process the M-Pesa callback data and update the MpesaTransaction and related Order.
    """
    try:
        print(callback_data)
        stk_callback = callback_data['Body']['stkCallback']
        checkout_request_id = stk_callback['CheckoutRequestID']
        result_code = stk_callback['ResultCode']
        result_desc = stk_callback['ResultDesc']
        metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
        
        # Extract transaction details
        amount = next((item['Value'] for item in metadata if item['Name'] == 'Amount'), 0)
        mpesa_receipt_number = next((item['Value'] for item in metadata if item['Name'] == 'MpesaReceiptNumber'), None)
        transaction_date = next((item['Value'] for item in metadata if item['Name'] == 'TransactionDate'), None)
        phone_number = next((item['Value'] for item in metadata if item['Name'] == 'PhoneNumber'), None)

        # Ensure transaction_date is in the correct format
        if transaction_date is not None:
            transaction_date = datetime.strptime(str(transaction_date), '%Y%m%d%H%M%S')
            transaction_date = timezone.make_aware(transaction_date, timezone.get_current_timezone())
        
        with transaction.atomic():
            mpesa_transaction = MpesaTransaction.objects.get(checkout_request_id=checkout_request_id)
            order = mpesa_transaction.order
            checkout_session = CheckoutSession.objects.get(order=order)

            print(checkout_session, 'checkout_session')
            print(checkout_session.mpesa_receipt_number, 'checkout_session.mpesa_receipt_number')
            print(checkout_request_id, 'checkout_request_id')

            if checkout_session.mpesa_receipt_number == checkout_request_id:
                raise HTTPException(status_code=400, detail="Callback already processed")

            if result_code == 0:
                checkout_session.mpesa_receipt_number = checkout_request_id
                checkout_session.transaction_date = transaction_date
                checkout_session.status = 'completed'

                mpesa_transaction.status = 'successful'
                mpesa_transaction.mpesa_receipt_number = mpesa_receipt_number
                mpesa_transaction.amount = amount
                mpesa_transaction.transaction_date = transaction_date
                mpesa_transaction.phone_number = phone_number
                mpesa_transaction.result_code = result_code
                mpesa_transaction.result_desc = result_desc
                order.status = 'processing'
                order.payment_status = 'paid'
                order.save()
                mpesa_transaction.save()
                checkout_session.save()
            else:
                mpesa_transaction.status = 'failed'
                mpesa_transaction.result_desc = result_desc
                mpesa_transaction.save()
        
        return {'status': 'success', 'message': 'Callback processed successfully'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}
    

def process_mpesa_query(checkout_request_id):
    """
    Check the status of a Lipa Na M-Pesa Online Payment.
    """
    business_shortcode = settings.MPESA_BUSINESS_SHORTCODE
    passkey = settings.MPESA_PASSKEY
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

    try:
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = generate_mpesa_password(business_shortcode, passkey, timestamp)
        
        CheckoutRequestID = checkout_request_id["checkout_request_id"]
        payload = {
            "BusinessShortCode": business_shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "CheckoutRequestID": CheckoutRequestID,
        }
        
        access_token = generate_mpesa_access_token()
        url = 'https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/query'
        headers = {
            'Authorization': f'Bearer {access_token}',
        }
        
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {'status': 'error', 'message': str(e)}

