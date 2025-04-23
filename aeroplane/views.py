from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404

from .models import (
    RATING, HolidayDeal, Product, Category, Cart, CartItem, CheckoutSession, Order, 
    OrderItem, ProductReview, MpesaTransaction
)

from users.models import (
  ShippingAddress, PaymentMethod
)

from .serializers import (
    HolidayDealSerializer, ProductSerializer, CategorySerializer, CartSerializer, CartItemSerializer, 
    CheckoutSessionSerializer, OrderSerializer, OrderItemSerializer, 
    ProductReviewSerializer, CheckoutSessionRequestSerializer, 
    CheckoutSessionResponseSerializer, MpesaQueryRequestSerializer, 
    MpesaQueryResponseSerializer
)
from .crud import (
    get_products, get_product, create_product, update_product, delete_product, 
    get_categories, get_products_by_category, get_or_create_cart, add_to_cart, 
    update_cart_it, remove_from_cart, create_checkout_session, create_pro_review, 
    get_product_reviews, update_product_review, delete_product_review, 
    initiate_mpesa_stk_push, process_mpesa_callback, process_mpesa_query
)
# from users.views import check_session_status

# request.user = check_session_status

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    def list(self, request):
        products = get_products()
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        product = get_product(pk)
        if not product:
            return Response({"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(product)
        return Response(serializer.data)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = create_product(**serializer.validated_data)
        return Response(self.get_serializer(product).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        product = update_product(pk, **request.data)
        if not product:
            return Response({"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(product)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        if not delete_product(pk):
            return Response({"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"message": "Product deleted successfully"}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='category/(?P<category_id>\d+)')
    def list_by_category(self, request, category_id=None):
        products = get_products_by_category(category_id)
        if not products:
            return Response({"detail": "No products found for this category"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    

class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user
        cart = get_or_create_cart(user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def create(self, request):
        user = request.user
        cart = get_or_create_cart(user)
        item_data = CartItemSerializer(data=request.data)
        item_data.is_valid(raise_exception=True)
        validated_data = item_data.validated_data
        add_to_cart(cart=cart, product_id=validated_data['product_id'], quantity=validated_data.get('quantity', 1))        
        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        user = request.user
        cart = get_or_create_cart(user)
        cart = update_cart_it(cart, pk, **request.data)
        return Response(CartSerializer(cart).data)

    def destroy(self, request, pk=None):
        user = request.user
        cart = get_or_create_cart(user)
        if remove_from_cart(cart, pk):
            return Response({"message": "Item removed from cart"}, status=status.HTTP_200_OK)
        return Response({"detail": "Item not found in cart"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_checkout(request):
    user = request.user
    cart = get_or_create_cart(user)
    checkout_session = create_checkout_session(cart)
    serializer = CheckoutSessionSerializer(checkout_session)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    user = request.user
    cart = Cart.objects.filter(user=user, is_active=True).first()
    if not cart or not cart.items.exists():
        return Response({"detail": "Cart is empty or does not exist"}, status=status.HTTP_400_BAD_REQUEST)
    
    total_amount = sum(item.product.price * item.quantity for item in cart.items.all())
    order = Order.objects.create(user=user, total_amount=total_amount, status="pending", payment_status="unpaid")
    for item in cart.items.all():
        OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity, price=item.product.price, size=item.size)
    cart.is_active = False
    cart.save()
    return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_orders(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-created_at')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_checkout_session_view(request):
    serializer = CheckoutSessionRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = request.user
    
    order = get_object_or_404(Order, id=serializer.validated_data['order_id'], user=user)
    if order.payment_status != "unpaid":
        return Response({"detail": "Order already processed"}, status=status.HTTP_400_BAD_REQUEST)
    
    shipping_address = get_object_or_404(ShippingAddress, id=serializer.validated_data['shipping_address_id'], user=user)
    payment_method = get_object_or_404(PaymentMethod, id=serializer.validated_data['payment_method_id'], user=user)
    phone_number = serializer.validated_data['phone_number']
    
    if not phone_number.startswith('254'):
        return Response({"detail": "Invalid M-Pesa phone number"}, status=status.HTTP_400_BAD_REQUEST)
    
    callback_url = f"https://admin.mohacollection.co.ke/mpesa-callback/"
    mpesa_response = initiate_mpesa_stk_push(order, phone_number, float(order.total_amount), callback_url)
    response_serializer = CheckoutSessionResponseSerializer({
        'checkout_request_id': mpesa_response['CheckoutRequestID'],
        'merchant_request_id': mpesa_response['MerchantRequestID'],
        'response_code': mpesa_response['ResponseCode'],
        'response_description': mpesa_response['ResponseDescription'],
        'customer_message': mpesa_response['CustomerMessage']
    })
    return Response(response_serializer.data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def mpesa_callback_view(request):
    result = process_mpesa_callback(request.data)
    if result['status'] == 'error':
        return Response({"detail": result['message']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response({"status": "success", "message": result['message']})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def query_mpesa_view(request):
    serializer = MpesaQueryRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    result = process_mpesa_query(serializer.validated_data)
    if result.get('status') == 'error':
        return Response({"detail": result['message']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(MpesaQueryResponseSerializer(result).data)


# Product Review Endpoints
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_product_review(request, product_id):
    """
    Create a review for a specific product by the authenticated user.
    """
    serializer = ProductReviewSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Validate rating against RATING choices
    rating = serializer.validated_data['rating']
    if rating not in [choice[0] for choice in RATING]:
        return Response({"detail": "Invalid rating value"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        review = create_pro_review(
            user=request.user,
            product_id=product_id,
            data=serializer.validated_data
        )
        return Response(review, status=status.HTTP_201_CREATED)
    except ValueError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])  # Allow anyone to view reviews
def list_product_reviews(request, product_id):
    """
    Retrieve all reviews for a specific product.
    """
    reviews = get_product_reviews(product_id=product_id)
    serializer = ProductReviewSerializer(reviews, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_user_reviews(request):
    """
    Retrieve all reviews by the authenticated user.
    """
    reviews = get_product_reviews(user=request.user)
    serializer = ProductReviewSerializer(reviews, many=True)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_product_review_view(request, review_id):
    """
    Update an existing review by the authenticated user.
    """
    serializer = ProductReviewSerializer(data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if 'rating' in serializer.validated_data and serializer.validated_data['rating'] not in [choice[0] for choice in RATING]:
        return Response({"detail": "Invalid rating value"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        review = update_product_review(
            review_id=review_id,
            user=request.user,
            data=serializer.validated_data
        )
        return Response(ProductReviewSerializer(review).data)
    except ValueError as e:
        return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_product_review_view(request, review_id):
    """
    Delete a review by the authenticated user.
    """
    if delete_product_review(review_id, request.user):
        return Response({"message": "Review deleted successfully"}, status=status.HTTP_200_OK)
    return Response({"detail": "Review not found or unauthorized"}, status=status.HTTP_404_NOT_FOUND)

class HolidayDealViewSet(viewsets.ModelViewSet):
    queryset = HolidayDeal.objects.all()
    serializer_class = HolidayDealSerializer
    permission_classes = [AllowAny]
    lookup_field = 'deal_id'

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(is_active=True)        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        # Explicitly handle the detail view
        deal = self.get_object()
        serializer = self.get_serializer(deal)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='products')
    def get_products(self, request, deal_id=None):
        deal = self.get_object()
        products = deal.products.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
