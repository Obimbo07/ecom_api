from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from .models import BlacklistedToken
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()

class CustomJWTAuthentication(JWTAuthentication):
    def get_validated_token(self, raw_token):
        token = super().get_validated_token(raw_token)
        if BlacklistedToken.objects.filter(token=str(token)).exists():
            raise InvalidToken("Token is blacklisted")
        return token
    
class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Username parameter is used for email
        try:
            user = User.objects.get(email__iexact=username)
        except User.DoesNotExist:
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None