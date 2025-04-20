from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
import uuid
# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        db_table = 'USER'
    
class Seller(models.Model):
    seller_id = models.CharField(max_length=25,primary_key=True)
    seller_name = models.CharField(max_length=50,null=False)
    
    def __str__(self):
        return self.seller_name
    
    class Meta:
        verbose_name = "Seller"
        verbose_name_plural = "Seller"
        db_table = 'SELLER'
    
class Category(models.Model):
    CATEGORY_CHOICES = [
        ('men', 'Men'),
        ('women', 'Women'),
        ('kids', 'Kids'),
        ('unisex', 'Unisex'),
    ]
    
    name = models.CharField(max_length=50, choices=CATEGORY_CHOICES, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.get_name_display()

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        db_table = 'CATEGORY'

class Size(models.Model):
    name = models.CharField(max_length=10, unique=True)
    description = models.CharField(max_length=50, blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Size"
        verbose_name_plural = "Sizes"
        ordering = ['name']

class ProductSize(models.Model):
    SIZE_CHOICES = [
        ('XS', 'Extra Small'),
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
        ('XXL', 'Double Extra Large'),
        ('28-30', '28-30'),
        ('30-32', '30-32'),
        ('32-34', '32-34'),
        ('34-36', '34-36'),
        ('36-38', '36-38'),
        ('38-40', '38-40'),
        ('40-42', '40-42'),
        ('42-44', '42-44'),
        ('44-46', '44-46'),
        ('46-48', '46-48'),
        ('48-50', '48-50'),
        ('Free', 'Free Size'),
    ]
    
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='sizes')
    size = models.CharField(max_length=10, choices=SIZE_CHOICES)
    stock = models.IntegerField(default=0)
    price_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    class Meta:
        unique_together = ('product', 'size')
        verbose_name = "Product Size"
        verbose_name_plural = "Product Sizes"
        db_table = 'PRODUCT_SIZE'
    
    def __str__(self):
        return f"{self.product.product_name} - {self.get_size_display()}"

class Product(models.Model):
    PRODUCT_TYPE_CHOICES = [
        ('regular', 'Regular'),
        ('auction', 'Auction'),
    ]
    
    PRODUCT_CONDITION_CHOICES = [
        ('new', 'New'),
        ('used', 'Used'),
        ('refurbished', 'Refurbished'),
    ]
    
    def generate_product_id():
        return f"P{str(uuid.uuid4())[:8]}"
    
    product_id = models.CharField(max_length=25, primary_key=True, default=generate_product_id)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, null=True, blank=True)
    product_name = models.CharField(max_length=50, null=False)
    product_type = models.CharField(max_length=50, choices=PRODUCT_TYPE_CHOICES, default='regular')
    product_condition = models.CharField(max_length=50, choices=PRODUCT_CONDITION_CHOICES, null=False)
    description = models.CharField(max_length=255, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    quantity = models.IntegerField(null=False)
    review = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='products', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_available = models.BooleanField(default=True)
    warranty_period = models.IntegerField(null=True, blank=True)  # in months
    refurbishment_details = models.TextField(blank=True, null=True)  # for refurbished items
    thrift_condition_details = models.TextField(blank=True, null=True)  # for thrift items
    current_bid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # for auction items
    last_bid_time = models.DateTimeField(null=True, blank=True)  # for auction items
    auction_status = models.CharField(max_length=10, choices=[('Active', 'Active'), ('Ended', 'Ended')], default='Active')
    
    def __str__(self):
        return self.product_name
    
    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        db_table = 'PRODUCT'

class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    order_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    payment_method = models.CharField(max_length=20, default='COD')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Essential shipping fields for COD
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    address_line1 = models.CharField(max_length=100)
    address_line2 = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=10)
    country = models.CharField(max_length=50, default='India')
    
    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = str(uuid.uuid4())[:8]
        if not self.amount and hasattr(self, 'items'):
            self.amount = sum(item.total_price for item in self.items.all())
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Order {self.order_id} - {self.user.email}"
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'bidbuygo_order'

class Delivery(models.Model):
    DELIVERY_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('failed', 'Delivery Failed'),
        ('returned', 'Returned'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery')
    tracking_number = models.CharField(max_length=50, unique=True, default='TRACK-0000')
    courier_service = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=DELIVERY_STATUS_CHOICES, default='pending')
    estimated_delivery_date = models.DateField(null=True, blank=True)
    actual_delivery_date = models.DateField(null=True, blank=True)
    delivery_address = models.ForeignKey('Address', on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Delivery {self.tracking_number} - {self.order.order_id}"

    class Meta:
        verbose_name = "Delivery"
        verbose_name_plural = "Deliveries"

class Inventory(models.Model):
    inventory_id = models.CharField(max_length=25, primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    volume = models.CharField(max_length=50,null=False)
    location = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"Inventory for {self.product.product_name}"
    
    class Meta:
        verbose_name = "Inventory"
        verbose_name_plural = "Inventory"
        db_table = 'INVENTORY'
    
class Transaction(models.Model):
    TRANSACTION_STATUS = (
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded')
    )
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS, default='SUCCESS')
    payment_id = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Transaction for Order {self.order.order_id} - {self.status}"

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.email}"

    @property
    def total_price(self):
        cart_items = self.items.all()
        if not cart_items.exists():
            return 0
        return sum(item.total_price for item in cart_items)

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"
        db_table = 'CART'

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('cart', 'product', 'size')

    def __str__(self):
        return f"{self.quantity}x {self.product.product_name} (Size: {self.size})"

    @property
    def total_price(self):
        try:
            return float(self.product.price) * self.quantity
        except (TypeError, ValueError):
            return 0

class Bidding(models.Model):
    BID_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
        ('Won', 'Won'),
        ('Lost', 'Lost'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    bid_time = models.DateTimeField(auto_now_add=True)
    bid_amt = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    bid_status = models.CharField(max_length=50, choices=BID_STATUS_CHOICES, default='Pending')
    initial_bid_amt = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    auto_bid_limit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_auto_bid = models.BooleanField(default=False)
    bid_increment = models.DecimalField(max_digits=10, decimal_places=2, default=1.00)
    auction_end_time = models.DateTimeField(null=True, blank=True)
    is_winner = models.BooleanField(default=False)

    class Meta:
        unique_together = (('user', 'product', 'bid_time'),)
        constraints = [
            models.CheckConstraint(check=models.Q(bid_amt__gte=models.F('initial_bid_amt')), name='chk_bid_amt')
        ]
        verbose_name = "Bidding"
        verbose_name_plural = "Bidding"
        db_table = 'BIDDING'

    def __str__(self):
        return f"{self.user.username} bid {self.bid_amt} on {self.product.product_name}"
    
class ProductReview(models.Model):
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    review_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_verified_purchase = models.BooleanField(default=False)
    helpful_votes = models.IntegerField(default=0)
    images = models.ImageField(upload_to='review_images/', blank=True, null=True)

    class Meta:
        unique_together = (('user', 'product'),)
        verbose_name = "Product Review"
        verbose_name_plural = "Product Reviews"
        db_table = 'PRODUCT_REVIEW'

    def __str__(self):
        return f"Review by {self.user.username} for {self.product.product_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    size = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.quantity}x {self.product.product_name} ({self.size})"

    @property
    def total_price(self):
        return self.quantity * self.price

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"
        db_table = 'bidbuygo_orderitem'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile for {self.user.email}"

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        db_table = 'USER_PROFILE'

class Address(models.Model):
    ADDRESS_TYPE_CHOICES = [
        ('home', 'Home'),
        ('office', 'Office'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPE_CHOICES, default='home')
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    address_line1 = models.CharField(max_length=100)
    address_line2 = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=10)
    country = models.CharField(max_length=50, default='India')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} - {self.get_address_type_display()}"

    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Addresses"
        db_table = 'ADDRESS'
        ordering = ['-is_default', '-created_at']

class Tracking(models.Model):
    TRACKING_EVENT_CHOICES = [
        ('order_placed', 'Order Placed'),
        ('order_confirmed', 'Order Confirmed'),
        ('order_packed', 'Order Packed'),
        ('order_shipped', 'Order Shipped'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('delivery_failed', 'Delivery Failed'),
        ('return_initiated', 'Return Initiated'),
        ('return_completed', 'Return Completed'),
    ]

    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE, related_name='tracking_updates')
    event = models.CharField(max_length=50, choices=TRACKING_EVENT_CHOICES, default='order_placed')
    event_time = models.DateTimeField(default=timezone.now)
    additional_info = models.TextField(blank=True, null=True)
    is_customer_notified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.get_event_display()} - {self.event_time.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['-event_time']
        verbose_name = "Tracking Update"
        verbose_name_plural = "Tracking Updates"

class OTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"{self.email} - {self.otp}"

class UnverifiedUser(models.Model):
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Unverified User"
        verbose_name_plural = "Unverified Users"
        db_table = 'UNVERIFIED_USER'