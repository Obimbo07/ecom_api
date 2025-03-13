from rest_framework import serializers

from aeroplane.crud import encode_image_to_base64
from .models import (
    Product, ProductImages, Category, Cart, CartItem, CheckoutSession, 
    Order, OrderItem, ProductReview, MpesaTransaction
)

class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductImages
        fields = ['id', 'image', 'date']

    def get_image(self, obj):
        return encode_image_to_base64(obj.images)

class ProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    additional_images = ProductImageSerializer(many=True, source='p_images')

    class Meta:
        model = Product
        fields = ['id', 'title', 'price', 'old_price', 'category_id', 'description', 
                  'specifications', 'type', 'stock_count', 'life', 'image', 'additional_images']

    def get_image(self, obj):
        return encode_image_to_base64(obj.image)

class CategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'title', 'image']

    def get_image(self, obj):
        return encode_image_to_base64(obj.image)
class CartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()  # Must be writable
    quantity = serializers.IntegerField(default=1)
    size = serializers.CharField(max_length=10, default='M', allow_null=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity', 'size']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total']

    def get_total(self, obj):
        return sum(item.product.price * item.quantity for item in obj.items.all())

class CheckoutSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckoutSession
        fields = ['id', 'status']

class OrderItemSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source='product.title')

    class Meta:
        model = OrderItem
        fields = ['product_title', 'quantity', 'price', 'size']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'total_amount', 'status', 'payment_status', 'created_at', 'items']

class ProductReviewSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username')

    class Meta:
        model = ProductReview
        fields = ['id', 'user', 'product', 'rating', 'review_text', 'created_at', 'updated_at', 'is_approved']

class CheckoutSessionRequestSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    shipping_address_id = serializers.IntegerField()
    payment_method_id = serializers.IntegerField()
    phone_number = serializers.CharField()

class CheckoutSessionResponseSerializer(serializers.Serializer):
    checkout_request_id = serializers.CharField()
    merchant_request_id = serializers.CharField()
    response_code = serializers.CharField()
    response_description = serializers.CharField()
    customer_message = serializers.CharField()

class MpesaQueryRequestSerializer(serializers.Serializer):
    checkout_request_id = serializers.CharField()

class MpesaQueryResponseSerializer(serializers.Serializer):
    ResponseCode = serializers.CharField()
    ResponseDescription = serializers.CharField()
    MerchantRequestID = serializers.CharField()
    CheckoutRequestID = serializers.CharField()
    ResultCode = serializers.CharField()
    ResultDesc = serializers.CharField()