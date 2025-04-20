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

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user', 'amount', 'status', 'payment_method', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_id', 'user__email', 'full_name', 'phone_number')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Order Information', {
            'fields': ('order_id', 'user', 'amount', 'status', 'payment_method')
        }),
        ('Shipping Information', {
            'fields': ('full_name', 'phone_number', 'address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(Bidding)
class BiddingAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'bid_amt', 'bid_status', 'bid_time')
    search_fields = ('user__username', 'product__product_name')
    readonly_fields = ('bid_time',)

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__email', 'product__product_name', 'review_text')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('order', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order__order_id',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ('seller_name',)
    search_fields = ('seller_name',)

@admin.register(ProductSize)
class ProductSizeAdmin(admin.ModelAdmin):
    list_display = ('product', 'size', 'stock', 'price_adjustment')
    list_filter = ('size',)
    search_fields = ('product__product_name',)
    list_editable = ('stock', 'price_adjustment')
