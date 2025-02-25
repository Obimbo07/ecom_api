from typing import List, Optional
from django.db import transaction
from .models import Cart, CartItem, Category, CheckoutSession, Product  # Assuming Product is one of your models

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