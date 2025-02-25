from django.contrib import admin
from .models import Cart, CartItem, Category, CheckoutSession, MpesaTransaction, Order, OrderItem, Tag, Product, ProductImages
from django.utils.safestring import mark_safe

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('cid', 'title', 'category_image')
    search_fields = ['title']
    # Since category_image is a method, we need to make it displayable in admin
    # By defining it in list_display, Django will automatically call it

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ['name']

class ProductImagesInline(admin.TabularInline):
    model = ProductImages
    extra = 1
   
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImagesInline]
    list_display = ('pid', 'title', 'price', 'old_price', 'category', 'product_status', 'status', 'in_stock', 'featured', 'digital', 'date', 'updated', 'product_image')
    list_filter = ('product_status', 'status', 'in_stock', 'featured', 'digital')
    search_fields = ['title', 'description']
    
    filter_horizontal = ('tags',)

    exclude = ['sku']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_active')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'status')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'quantity', 'price', 'size')

# Register CheckoutSession model
@admin.register(CheckoutSession)
class CheckoutSessionAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'created_at')

@admin.register(MpesaTransaction)
class MpesaTransactionAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'amount')
