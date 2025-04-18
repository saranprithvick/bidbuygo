from django.contrib import admin
from .models import *

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'product_type', 'product_condition', 'price', 'quantity', 'is_available')
    list_filter = ('product_type', 'product_condition', 'category', 'is_available')
    search_fields = ('product_name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('product_name', 'product_type', 'product_condition', 'description', 'category')
        }),
        ('Pricing and Inventory', {
            'fields': ('price', 'quantity', 'is_available')
        }),
        ('Additional Details', {
            'fields': ('warranty_period', 'refurbishment_details', 'thrift_condition_details')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user', 'product', 'price_amt', 'order_status', 'order_date')
    list_filter = ('order_status', 'order_date')
    search_fields = ('order_id', 'user__username', 'product__product_name')
    readonly_fields = ('order_date',)

class BiddingAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'bid_amt', 'bid_status', 'bid_time')
    list_filter = ('bid_status', 'is_auto_bid')
    search_fields = ('user__username', 'product__product_name')
    readonly_fields = ('bid_time',)

class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'created_at', 'is_verified_purchase')
    list_filter = ('rating', 'is_verified_purchase')
    search_fields = ('user__username', 'product__product_name', 'review_text')

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'order', 'transaction_amt', 'mode_of_payment')
    search_fields = ('transaction_id', 'order__order_id')
    readonly_fields = ('transaction_id',)

class SellerAdmin(admin.ModelAdmin):
    list_display = ('seller_name',)
    search_fields = ('seller_name',)

# Register models with their custom admin classes
admin.site.register(Product, ProductAdmin)
admin.site.register(Orders, OrderAdmin)
admin.site.register(Bidding, BiddingAdmin)
admin.site.register(ProductReview, ProductReviewAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Seller, SellerAdmin)
admin.site.register(Delivery)
admin.site.register(Tracking)
admin.site.register(Inventory)
