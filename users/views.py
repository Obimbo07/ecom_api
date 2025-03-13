from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from django.contrib.auth import authenticate, get_user_model
from django.conf import settings
from .serializers import (LoginRequestSerializer, RegisterRequestSerializer, 
                         ShippingAddressSerializer, PaymentMethodSerializer, UserProfileSerializer)
from .models import BlacklistedToken, ShippingAddress, PaymentMethod
from .crud import (create_shipping_address, get_shipping_addresses, update_shipping_address, 
                   delete_shipping_address, create_payment_method, get_payment_methods, 
                   update_payment_method, delete_payment_method)

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = RegisterRequestSerializer(data=request.data)
    if serializer.is_valid():
        if User.objects.filter(username=serializer.validated_data['username']).exists():
            return Response({"detail": "Username already taken"}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=serializer.validated_data['email']).exists():
           return Response({"detail": "Email already taken"}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.create_user(
            username=serializer.validated_data['username'],
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    serializer = LoginRequestSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = authenticate(username=username, password=password)
        if not user:
            return Response({"detail": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)
        token = AccessToken.for_user(user)
        refresh = RefreshToken.for_user(user)
        return Response({"access_token": str(token), "refresh_token": str(refresh)}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    token = request.auth  # JWT token from Authorization header
    if not token:
        return Response({"detail": "Token missing"}, status=status.HTTP_403_FORBIDDEN)
    if not BlacklistedToken.objects.filter(token=str(token)).exists():
        BlacklistedToken.objects.create(token=str(token))
    return Response({"message": "Logout successful. Token invalidated."}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_session_status(request):
    return Response({"message": "Session is active", "user": request.user.username}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)

class ShippingAddressViewSet(viewsets.ModelViewSet):
    serializer_class = ShippingAddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ShippingAddress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        update_shipping_address(instance.id, request.user, serializer.validated_data)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if delete_shipping_address(instance.id, request.user):
            return Response({"message": "Shipping address deleted successfully"}, status=status.HTTP_200_OK)
        return Response({"detail": "Shipping address not found"}, status=status.HTTP_404_NOT_FOUND)

class PaymentMethodViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PaymentMethod.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        update_payment_method(instance.id, request.user, serializer.validated_data)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if delete_payment_method(instance.id, request.user):
            return Response({"message": "Payment method deleted successfully"}, status=status.HTTP_200_OK)
        return Response({"detail": "Payment method not found"}, status=status.HTTP_404_NOT_FOUND)