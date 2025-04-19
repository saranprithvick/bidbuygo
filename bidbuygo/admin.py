from django.contrib import admin
from .models import *

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')
    ordering = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'size', 'quantity', 'product_type', 'product_condition', 'auction_status')
    list_filter = ('category', 'product_type', 'product_condition', 'auction_status', 'size')
    search_fields = ('name', 'description', 'size')
    list_editable = ('price', 'quantity', 'size')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'category', 'image')
        }),
        ('Pricing and Inventory', {
            'fields': ('price', 'quantity', 'size')
        }),
        ('Product Details', {
            'fields': ('product_type', 'product_condition')
        }),
        ('Auction Settings', {
            'fields': ('auction_status', 'last_bid_time'),
            'classes': ('collapse',)
        })
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

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'order', 'amount', 'mode_of_payment', 'status', 'created_at']
    list_filter = ['status', 'mode_of_payment', 'created_at']
    readonly_fields = ['payment_id', 'refund_id', 'created_at', 'updated_at']
    search_fields = ['payment_id', 'order__id', 'order__user__username']
    date_hierarchy = 'created_at'

class SellerAdmin(admin.ModelAdmin):
    list_display = ('seller_name',)
    search_fields = ('seller_name',)

# Register models with their custom admin classes
admin.site.register(Orders, OrderAdmin)
admin.site.register(Bidding, BiddingAdmin)
admin.site.register(ProductReview, ProductReviewAdmin)
admin.site.register(Seller, SellerAdmin)
admin.site.register(Delivery)
admin.site.register(Tracking)
admin.site.register(Inventory)
