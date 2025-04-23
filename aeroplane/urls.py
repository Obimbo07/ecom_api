from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from aeroplane.views import (
    HolidayDealViewSet, ProductViewSet, CategoryViewSet, CartViewSet, create_checkout, 
    create_order, get_user_orders, create_checkout_session_view, 
    mpesa_callback_view, query_mpesa_view,
    # New review endpoints
    create_product_review, list_product_reviews, list_user_reviews, 
    update_product_review, delete_product_review
)

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'holiday-deals', HolidayDealViewSet, basename='holiday-deal')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('users/', include('users.urls')),
    path('api/checkout/', create_checkout),
    path('api/orders/', create_order),
    path('api/user/orders/', get_user_orders),
    path('api/checkout-session/', create_checkout_session_view),
    path('mpesa-callback/', mpesa_callback_view),
    path('api/query-mpesa/', query_mpesa_view),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Add this
    # Product Review Endpoints
    path('api/products/<int:product_id>/reviews/', list_product_reviews, name='product-reviews'),
    path('api/products/<int:product_id>/reviews/create/', create_product_review, name='create-product-review'),
    path('api/users/reviews/', list_user_reviews, name='user-reviews'),
    path('api/reviews/<int:review_id>/', update_product_review, name='update-review'),
    path('api/reviews/<int:review_id>/delete/', delete_product_review, name='delete-review'),
]