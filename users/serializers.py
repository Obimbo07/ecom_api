from rest_framework import serializers

from aeroplane.crud import encode_image_to_base64
from .models import User, ShippingAddress, PaymentMethod, BlacklistedToken, Profile

class LoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128, write_only=True)

class RegisterRequestSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField()

class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = ['id', 'full_name', 'address_line1', 'address_line2', 'city', 'state', 
                  'postal_code', 'country', 'phone', 'is_default', 'created_at', 'updated_at']

class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ['id', 'method_type', 'phone_number', 'last_four', 'is_default', 
                  'created_at', 'updated_at']

class ProfileSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Profile
        fields = ['image', 'full_name', 'bio', 'phone', 'verified']
        read_only_fields = ['verified']

    def get_image(self, obj):
        if obj.image:
            return encode_image_to_base64(obj.image)
        return None

class UserProfileSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'bio', 'profile']
        read_only_fields = ['id', 'username']

    def get_image(self, obj):
        if obj.image:
            return encode_image_to_base64(obj.image)
        return None

    def to_representation(self, instance):
        # Ensure the profile exists before serializing
        if not hasattr(instance, 'profile') or instance.profile is None:
            # If no profile exists, create one or return an empty dict for the field
            Profile.objects.get_or_create(user=instance)
        return super().to_representation(instance)

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        print(f"Profile data: {profile_data}")
        instance.email = validated_data.get('email', instance.email)
        instance.bio = validated_data.get('bio', instance.bio)
        instance.save()

        profile, _ = Profile.objects.get_or_create(user=instance)
        profile.full_name = profile_data.get('full_name', profile.full_name)
        profile.bio = profile_data.get('bio', profile.bio)
        profile.phone = profile_data.get('phone', profile.phone)
        if 'image' in profile_data:
            print(f"Image data: {profile_data['image']}")
            profile.image = profile_data['image']
        profile.save()

        return instance