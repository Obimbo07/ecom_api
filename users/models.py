from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save

# Create your models here.
class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=20, unique=True)
    bio= models.CharField(max_length=300, blank=True, null=True)

    def __str__(self):
        return self.username
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="user-profile")
    full_name = models.CharField(max_length=200, null=True, blank=True)
    bio = models.CharField(max_length=300, null=True, blank=True)
    phone = models.IntegerField(null=True, blank=True)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.full_name} - {self.bio}"

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)

class BlacklistedToken(models.Model):
    token = models.TextField(unique=True)
    blacklisted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Blacklisted {self.token[:10]}..."
    

class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shipping_addresses')
    full_name = models.CharField(max_length=200, null=True, blank=True)
    address_line1 = models.CharField(max_length=200)
    address_line2 = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, null=True, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} - {self.address_line1}, {self.city}, {self.country}"

class PaymentMethod(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_methods')
    method_type = models.CharField(max_length=50, default='mpesa')  # Default to Mpesa
    phone_number = models.CharField(max_length=20, null=True, blank=True)  # Mpesa phone number
    last_four = models.CharField(max_length=4, null=True, blank=True)  # For cards, but can be blank for Mpesa
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.method_type == 'mpesa':
            return f"Mpesa - {self.phone_number}"
        return f"{self.method_type.upper()} ****{self.last_four}"