from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Profile, User, ShippingAddress, PaymentMethod

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Profile"

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    
@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    pass

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    pass
