from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (register_user, login_user, logout_user, check_session_status, 
                    get_user_profile, ShippingAddressViewSet, PaymentMethodViewSet)

router = DefaultRouter()
router.register(r'shipping-addresses', ShippingAddressViewSet, basename='shipping-address')
router.register(r'payment-methods', PaymentMethodViewSet, basename='payment-method')

urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('session/', check_session_status, name='session_status'),
    path('me/', get_user_profile, name='user_profile'),
    path('', include(router.urls)),
]