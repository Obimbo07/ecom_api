from typing import List
from django.db import transaction
from .models import Category, Product  # Assuming Product is one of your models

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