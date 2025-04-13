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
    seller = models.CharField(Seller,on_delete=models.CASCADE)
    product_name = models.CharField(max_length=50,null=False)
    product_type = models.CharField(max_length=50,blank=False,null=False)
    description = models.CharField(max_length=255,blank=True,null=True)
    price = models.DecimalField(max_digits=10,decimal_places=2)
    quantity = models.IntegerField(null=False)
    review = models.TextField(blank=True,null=True)

    def __str__(self):
        return self.product_name
    


