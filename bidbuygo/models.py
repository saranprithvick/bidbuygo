from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Seller(models.Model):
    seller_id = models.CharField(max_length=25,primary_key=True)
    seller_name = models.CharField(max_length=50,null=False)
    
    def __str__(self):
        return self.seller_name
    
class Product(models.Model):
    product_id = models.CharField(max_length=25,primary_key=True)
    seller = models.ForeignKey(Seller,on_delete=models.CASCADE)
    product_name = models.CharField(max_length=50,null=False)
    product_type = models.CharField(max_length=50,blank=False,null=False)
    description = models.CharField(max_length=255,blank=True,null=True)
    category = models.CharField(max_length=50, blank=True, null=True)
    price = models.DecimalField(max_digits=10,decimal_places=2)
    quantity = models.IntegerField(null=False)
    review = models.TextField(blank=True,null=True)

    def __str__(self):
        return self.product_name
    
class Orders(models.Model):
    order_id = models.CharField(max_length=25,primary_key=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    order_address = models.TextField()
    price_amt = models.DecimalField(max_digits=10,decimal_places=2)
    order_date = models.DateTimeField()
    order_status = models.CharField(max_length=50)

    def __str__(self):
        return f"Order {self.order_id}"
    
class Delivery(models.Model):
    delivery_id = models.CharField(max_length=25,primary_key=True)
    order = models.ForeignKey(Orders,on_delete=models.CASCADE)
    courier_service = models.CharField(max_length=50)
    tracking_id = models.CharField(max_length=25,unique=True)
    delivery_status = models.CharField(max_length=50)

    def __str__(self):
        return f"Delivery {self.delivery_id}"
    
class Tracking(models.Model):
    tracking_id = models.CharField(max_length=25, primary_key=True)
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE)

    def __str__(self):
        return self.tracking_id
    
class Inventory(models.Model):
    inventory_id = models.CharField(max_length=25, primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    volume = models.CharField(max_length=50)
    location = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"Inventory for {self.product.product_name}"
    
class Transaction(models.Model):
    transaction_id = models.CharField(max_length=25, primary_key=True)
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    transaction_amt = models.DecimalField(max_digits=10, decimal_places=2)
    account_details = models.CharField(max_length=255)
    mode_of_payment = models.CharField(max_length=50)

    def __str__(self):
        return f"Transaction {self.transaction_id} for Order {self.order.order_id}"
    
class Bidding(models.Model):
    BID_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    bid_time = models.DateTimeField()
    bid_amt = models.DecimalField(max_digits=10, decimal_places=2)
    bid_status = models.CharField(max_length=50, choices=BID_STATUS_CHOICES)
    initial_bid_amt = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        unique_together = (('user', 'product', 'bid_time'),)
        constraints = [
            models.CheckConstraint(check=models.Q(bid_amt__gte=models.F('initial_bid_amt')), name='chk_bid_amt')
        ]

    def __str__(self):
        return f"{self.user.username} bid {self.bid_amt} on {self.product.product_name}"
    

    


