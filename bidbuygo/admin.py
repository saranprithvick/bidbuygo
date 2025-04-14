from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import User, Seller, Product, Orders, Delivery, Tracking, Inventory, Bidding, Transaction

#admin.site.register(User)
admin.site.register(Seller)
admin.site.register(Product)
admin.site.register(Orders)
admin.site.register(Delivery)
admin.site.register(Tracking)
admin.site.register(Inventory)
admin.site.register(Bidding)
admin.site.register(Transaction)
