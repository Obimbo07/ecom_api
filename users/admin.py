from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, ShippingAddress, PaymentMethod

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    pass

@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    pass

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    pass
