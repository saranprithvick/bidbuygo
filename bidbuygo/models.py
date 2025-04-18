from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class User(models.Model):
    user_id = models.CharField(max_length=25, primary_key=True)
    user_name = models.CharField(max_length=255,null=False)
    password = models.CharField(max_length=255,null=False)
    email = models.EmailField(unique=True,null=False)
    mobile_number = models.CharField(max_length=13, unique=True,null=False)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.user_name
    
class Seller(models.Model):
    seller_id = models.CharField(max_length=25,primary_key=True)
    seller_name = models.CharField(max_length=50,null=False)
    
    def __str__(self):
        return self.seller_name
    
    class Meta:
        verbose_name = "Seller"
        verbose_name_plural = "Seller"
        db_table = 'SELLER'
    
class Product(models.Model):
    PRODUCT_CONDITION_CHOICES = [
        ('New', 'New'),
        ('Refurbished', 'Refurbished'),
        ('Used', 'Used'),
    ]
    
    PRODUCT_TYPE_CHOICES = [
        ('Regular', 'Regular'),
        ('Thrift', 'Thrift'),
        ('Auction', 'Auction'),
    ]
    
    product_id = models.CharField(max_length=25,primary_key=True)
    seller = models.ForeignKey(Seller,on_delete=models.CASCADE)
    product_name = models.CharField(max_length=50,null=False)
    product_type = models.CharField(max_length=50, choices=PRODUCT_TYPE_CHOICES, default='Regular')
    product_condition = models.CharField(max_length=50, choices=PRODUCT_CONDITION_CHOICES, null=False)
    description = models.CharField(max_length=255,blank=True,null=True)
    category = models.CharField(max_length=50, blank=True,null=True)
    price = models.DecimalField(max_digits=10,decimal_places=2,null=False)
    quantity = models.IntegerField(null=False)
    review = models.TextField(blank=True,null=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_available = models.BooleanField(default=True)
    warranty_period = models.IntegerField(null=True, blank=True)  # in months
    refurbishment_details = models.TextField(blank=True, null=True)  # for refurbished items
    thrift_condition_details = models.TextField(blank=True, null=True)  # for thrift items

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
    transaction_id = models.CharField(max_length=25, primary_key=True)
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    transaction_amt = models.DecimalField(max_digits=10, decimal_places=2,null=False)
    account_details = models.CharField(max_length=255,null=False)
    mode_of_payment = models.CharField(max_length=50,null=False)

    def __str__(self):
        return f"Transaction {self.transaction_id} for Order {self.order.order_id}"
    
    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transaction"
        db_table = 'TRANSACTION'
    
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

    def __str__(self):
        return f"{self.user.username} bid {self.bid_amt} on {self.product.product_name}"
    
    class Meta:
        verbose_name = "Bidding"
        verbose_name_plural = "Bidding"
        db_table = 'BIDDING'
    
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

    


