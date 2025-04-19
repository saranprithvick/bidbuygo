from django.contrib import admin
from .models import *

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')
    ordering = ('name',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)

class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'category', 'price', 'quantity', 'product_type', 'product_condition', 'auction_status')
    list_filter = ('category', 'product_type', 'product_condition', 'auction_status')
    search_fields = ('product_name', 'description')
    list_editable = ('price', 'quantity')
    inlines = [ProductSizeInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('product_name', 'description', 'category', 'image')
        }),
        ('Pricing and Inventory', {
            'fields': ('price', 'quantity')
        }),
        ('Product Details', {
            'fields': ('product_type', 'product_condition', 'warranty_period', 'refurbishment_details', 'thrift_condition_details')
        }),
        ('Auction Settings', {
            'fields': ('auction_status', 'last_bid_time', 'current_bid'),
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

@admin.register(ProductSize)
class ProductSizeAdmin(admin.ModelAdmin):
    list_display = ('product', 'size', 'stock', 'price_adjustment')
    list_filter = ('size',)
    search_fields = ('product__product_name',)
    list_editable = ('stock', 'price_adjustment')

# Register models with their custom admin classes
admin.site.register(Orders, OrderAdmin)
admin.site.register(Bidding, BiddingAdmin)
admin.site.register(ProductReview, ProductReviewAdmin)
admin.site.register(Seller, SellerAdmin)
admin.site.register(Delivery)
admin.site.register(Tracking)
admin.site.register(Inventory)
