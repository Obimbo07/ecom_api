from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from aeroplane.views import (
    ProductViewSet, CategoryViewSet, CartViewSet, create_checkout, 
    create_order, get_user_orders, create_checkout_session_view, 
    mpesa_callback_view, query_mpesa_view
)

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'cart', CartViewSet, basename='casrt')

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
]