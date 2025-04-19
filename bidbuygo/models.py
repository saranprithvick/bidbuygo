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

class Orders(models.Model):
    order_id = models.CharField(max_length=25,primary_key=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    order_address = models.TextField(null=False)
    price_amt = models.DecimalField(max_digits=10,decimal_places=2,null=False)
    order_date = models.DateTimeField(null=False)
    order_status = models.CharField(max_length=50,null=False)

    def __str__(self):
        return f"Order {self.order_id} by {self.user.username}"
    
    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        db_table = 'ORDERS'
    
class Delivery(models.Model):
    delivery_id = models.CharField(max_length=25,primary_key=True)
    order = models.ForeignKey(Orders,on_delete=models.CASCADE)
    courier_service = models.CharField(max_length=50,null=False)
    tracking_id = models.CharField(max_length=25,unique=True,null=False)
    delivery_status = models.CharField(max_length=50,null=False)

    def __str__(self):
        return f"Delivery {self.delivery_id}"
    
    class Meta:
        verbose_name = "Delivery"
        verbose_name_plural = "Delivery"
        db_table = 'DELIVERY'
    
class Tracking(models.Model):
    tracking_id = models.CharField(max_length=25, primary_key=True)
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE)

    def __str__(self):
        return self.tracking_id
    
    class Meta:
        verbose_name = "Tracking"
        verbose_name_plural = "Tracking"
        db_table = 'TRACKING'
    
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
    
class Order(models.Model):
    ORDER_STATUS = (
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded')
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='PENDING')
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order {self.id} - {self.user.username}"

class Transaction(models.Model):
    TRANSACTION_STATUS = (
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded')
    )
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100, default='')
    refund_id = models.CharField(max_length=100, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS, default='FAILED')
    mode_of_payment = models.CharField(max_length=50, default='RAZORPAY')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Transaction {self.payment_id} - {self.status}"

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.email}"

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"
        db_table = 'CART'

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.quantity}x {self.product.product_name} in {self.cart}"

    class Meta:
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"
        db_table = 'CART_ITEM'
        unique_together = ('cart', 'product')

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