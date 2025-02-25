from .models import ShippingAddress, PaymentMethod

def create_shipping_address(user, data):
    return ShippingAddress.objects.create(user=user, **data)

def get_shipping_addresses(user):
    return ShippingAddress.objects.filter(user=user)

def update_shipping_address(address_id, user, data):
    address = ShippingAddress.objects.filter(id=address_id, user=user).first()
    if not address:
        raise ValueError("Shipping address not found")
    for key, value in data.items():
        setattr(address, key, value)
    address.save()
    return address

def delete_shipping_address(address_id, user):
    address = ShippingAddress.objects.filter(id=address_id, user=user).first()
    if not address:
        raise ValueError("Shipping address not found")
    address.delete()
    return True

def create_payment_method(user, data):
    return PaymentMethod.objects.create(user=user, **data)

def get_payment_methods(user):
    return PaymentMethod.objects.filter(user=user)

def update_payment_method(method_id, user, data):
    method = PaymentMethod.objects.filter(id=method_id, user=user).first()
    if not method:
        raise ValueError("Payment method not found")
    for key, value in data.items():
        setattr(method, key, value)
    method.save()
    return method

def delete_payment_method(method_id, user):
    method = PaymentMethod.objects.filter(id=method_id, user=user).first()
    if not method:
        raise ValueError("Payment method not found")
    method.delete()
    return True