from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from shortuuidfield import ShortUUIDField
from users.models import User
from django.utils.safestring import mark_safe
from django_ckeditor_5.fields import CKEditor5Field
from django.core.validators import MinValueValidator, MaxValueValidator
STATUS_CHOICE = (
    ("processing", "Processing"),
    ("shipped", "Shipped"),
    ("delivered", "Delivered"),
)

PAYMENT_CHOICE = (
    ("draft", "Draft"),
    ("completed", "Completed"),
    ("failed", "Failed"),
    ("cancelled", "Cancelled"),
    ("over-pay", "Over pay"),
)

STATUS = (
    ("draft", "Draft"),
    ("disabled", "Disabled"),
    ("rejected", "Rejected"),
    ("in_review", "In Review"),
    ("published", "Published"),
)

RATING = (
    ( 1,  "★☆☆☆☆"),
    ( 2,  "★★☆☆☆"),
    ( 3,  "★★★☆☆"),
    ( 4,  "★★★★☆"),
    ( 5,  "★★★★★"),
)

def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.user.id, filename)

class Category(models.Model):
    cid = ShortUUIDField(unique=True, max_length=20)
    title = models.CharField(max_length=100, default="shirt")
    image = models.ImageField(upload_to="category", default="category.jpg")

    class Meta:
        verbose_name_plural = "Categories"

    def category_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

    def __str__(self):
        return self.title

class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    pid = ShortUUIDField(unique=True, max_length=20)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="category")
    title = models.CharField(max_length=100, default="Fresh Pear")
    image = models.ImageField(upload_to=user_directory_path, default="product.jpg")
    description = CKEditor5Field(null=True, blank=True, default="This is the product")
    price = models.DecimalField(max_digits=12, decimal_places=2, default="1.99")
    old_price = models.DecimalField(max_digits=12, decimal_places=2, default="2.99")
    specifications = CKEditor5Field(null=True, blank=True)
    type = models.CharField(max_length=100, default="Organic", null=True, blank=True)
    stock_count = models.CharField(max_length=100, default="10", null=True, blank=True)
    life = models.CharField(max_length=100, default="100 Days", null=True, blank=True)
    mfd = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    product_status = models.CharField(choices=STATUS, max_length=10, default="in_review")
    status = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    digital = models.BooleanField(default=False)
    sku = ShortUUIDField(unique=True, max_length=10)
    date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Products"

    def product_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

    def __str__(self):
        return self.title

    def get_precentage(self):
        new_price = (self.price / self.old_price) * 100
        return new_price


class ProductImages(models.Model):
    images = models.ImageField(upload_to="product-images", default="product.jpg")
    product = models.ForeignKey(Product, related_name="p_images", on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Product Images"

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"

    def __str__(self):
        return f"Cart for {self.user.username if self.user else 'Guest'}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=10, default='M')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"

    def __str__(self):
        return f"{self.quantity} x {self.product.title} (Size: {self.size})"
    

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    )
    PAYMENT_STATUS_CHOICES = (
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at the time of order
    size = models.CharField(max_length=20, blank=True, null=True)  # Optional, if applicable

    def __str__(self):
        return f"{self.product.title} (x{self.quantity})"

class CheckoutSession(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    mpesa_receipt_number = models.CharField(max_length=255, null=True, blank=True)  # For M-Pesa
    transaction_date = models.DateTimeField(null=True, blank=True)  # For M-Pesa
    status = models.CharField(max_length=50, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Checkout Session for Order {self.order.id}"
    def __str__(self):
        return f"Checkout Session for Order {self.order.id}"
    

class ProductReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(choices=RATING)  # Use your existing RATING choices
    review_text = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=False)  # Optional: admin approval for reviews

    def __str__(self):
        return f"Review by {self.user.username} for {self.product.title} ({self.rating} stars)"


from django.utils import timezone
from .models import CheckoutSession

class MpesaTransaction(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='mpesa_transaction')
    checkout_session = models.OneToOneField(CheckoutSession, on_delete=models.CASCADE, null=True, blank=True, related_name='mpesa_transaction')
    merchant_request_id = models.CharField(max_length=255, unique=True)
    checkout_request_id = models.CharField(max_length=255, unique=True)
    mpesa_receipt_number = models.CharField(max_length=255, null=True, blank=True)
    transaction_date = models.DateTimeField(null=True, blank=True)
    phone_number = models.CharField(max_length=12)  # M-Pesa phone number format (e.g., 2547XXXXXXXX)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    result_code = models.IntegerField(null=True, blank=True)  # M-Pesa result code (0 for success, others for errors)
    result_desc = models.CharField(max_length=255, null=True, blank=True)  # Description of the result
    status = models.CharField(max_length=50, default='pending')  # e.g., 'pending', 'successful', 'failed'
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"M-Pesa Transaction for Order {self.order.id} - {self.status}"

    class Meta:
        verbose_name = "M-Pesa Transaction"
        verbose_name_plural = "M-Pesa Transactions"

class HolidayDeal(models.Model):
    # Unique identifier for the deal
    deal_id = ShortUUIDField(unique=True, max_length=20)
    
    # Name of the holiday/deal (e.g., "Ramadan Sale", "Idd Special")
    name = models.CharField(max_length=100, unique=True, help_text=_("Name of the holiday deal (e.g., Ramadan Sale)"))
    
    # Description of the deal
    description = models.TextField(null=True, blank=True, help_text=_("Optional description of the deal"))
    
    # Products associated with this deal
    products = models.ManyToManyField(Product, related_name='holiday_deals', help_text=_("Products included in this deal"))
    
    # Discount percentage (0-100%)
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_("Discount percentage off the product price (0-100)")
    )
    
    # Start and end dates for the deal
    start_date = models.DateTimeField(help_text=_("Start date and time of the deal"))
    end_date = models.DateTimeField(help_text=_("End date and time of the deal"))
    
    # Active status (automatically managed based on dates)
    is_active = models.BooleanField(default=False, editable=False, help_text=_("Automatically set based on start/end dates"))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Holiday Deal"
        verbose_name_plural = "Holiday Deals"
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.name} ({self.discount_percentage}% off)"

    def save(self, *args, **kwargs):
        """Override save to update is_active based on current date."""
        now = timezone.now()
        self.is_active = self.start_date <= now <= self.end_date
        super().save(*args, **kwargs)

    def get_discounted_price(self, product):
        """Calculate the discounted price for a given product."""
        if self.is_active:
            discount = (self.discount_percentage / 100) * product.price
            return product.price - discount
        return product.price

    @property
    def is_expired(self):
        """Check if the deal has expired."""
        return timezone.now() > self.end_date

    @property
    def is_upcoming(self):
        """Check if the deal is yet to start."""
        return timezone.now() < self.start_date