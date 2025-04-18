from django.core.management.base import BaseCommand
from bidbuygo.models import Product, User, Seller
import uuid
from decimal import Decimal
from django.contrib.auth.hashers import make_password
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Populates the database with sample clothing data'

    def handle(self, *args, **kwargs):
        # Create multiple sellers
        sellers = {
            'fashion_hub': Seller.objects.get_or_create(
                seller_id=str(uuid.uuid4())[:8],
                seller_name="FashionHub"
            )[0],
            'vintage_vault': Seller.objects.get_or_create(
                seller_id=str(uuid.uuid4())[:8],
                seller_name="Vintage Vault"
            )[0],
            'luxury_lane': Seller.objects.get_or_create(
                seller_id=str(uuid.uuid4())[:8],
                seller_name="Luxury Lane"
            )[0],
            'eco_fashion': Seller.objects.get_or_create(
                seller_id=str(uuid.uuid4())[:8],
                seller_name="Eco Fashion"
            )[0]
        }

        # Get or create admin user
        admin_user = User.objects.filter(email="admin@example.com").first()
        if not admin_user:
            admin_user = User.objects.create(
                user_id=str(uuid.uuid4())[:8],
                user_name="admin",
                email="admin@example.com",
                password=make_password('admin123'),
                mobile_number='9876543210',
                address='Admin Address'
            )

        # First, delete existing products
        Product.objects.all().delete()

        # Sample clothing products with image paths and different sellers
        clothing_products = [
            {
                'product_name': 'Classic White T-Shirt',
                'product_type': 'Regular',
                'product_condition': 'New',
                'description': '100% cotton white t-shirt, perfect for everyday wear',
                'category': 'Tops',
                'price': Decimal('24.99'),
                'quantity': 100,
                'warranty_period': 30,
                'seller': sellers['fashion_hub'],
                'image': 'products/white_tshirt.jpg'
            },
            {
                'product_name': 'Vintage Slim Fit Jeans',
                'product_type': 'Thrift',
                'product_condition': 'Good',
                'description': 'Authentic vintage blue denim jeans with slim fit design',
                'category': 'Bottoms',
                'price': Decimal('29.99'),
                'quantity': 30,
                'warranty_period': 0,
                'refurbishment_details': 'Lightly worn, professionally cleaned',
                'thrift_condition_details': 'Minor wear on knees, otherwise good condition',
                'seller': sellers['vintage_vault'],
                'image': 'products/slim_jeans.jpg'
            },
            {
                'product_name': 'Designer Oversized Hoodie',
                'product_type': 'Regular',
                'product_condition': 'New',
                'description': 'Premium quality oversized hoodie with designer logo',
                'category': 'Outerwear',
                'price': Decimal('89.99'),
                'quantity': 50,
                'warranty_period': 30,
                'seller': sellers['luxury_lane'],
                'image': 'products/hoodie.jpg'
            },
            {
                'product_name': 'Vintage Floral Dress',
                'product_type': 'Auction',
                'product_condition': 'Like New',
                'description': 'Rare vintage floral print summer dress from the 80s',
                'category': 'Dresses',
                'price': Decimal('49.99'),
                'quantity': 1,
                'warranty_period': 0,
                'refurbishment_details': 'Professionally restored',
                'thrift_condition_details': 'Excellent vintage condition',
                'seller': sellers['vintage_vault'],
                'image': 'products/floral_dress.jpg'
            },
            {
                'product_name': 'Premium Leather Jacket',
                'product_type': 'Regular',
                'product_condition': 'New',
                'description': 'Genuine leather jacket with premium craftsmanship',
                'category': 'Outerwear',
                'price': Decimal('199.99'),
                'quantity': 20,
                'warranty_period': 90,
                'seller': sellers['luxury_lane'],
                'image': 'products/leather_jacket.jpg'
            },
            {
                'product_name': 'Eco-Friendly Sweater',
                'product_type': 'Regular',
                'product_condition': 'New',
                'description': 'Sustainable wool blend sweater, ethically produced',
                'category': 'Tops',
                'price': Decimal('79.99'),
                'quantity': 40,
                'warranty_period': 30,
                'seller': sellers['eco_fashion'],
                'image': 'products/striped_sweater.jpg'
            },
            {
                'product_name': 'Vintage Designer Skirt',
                'product_type': 'Auction',
                'product_condition': 'Good',
                'description': 'Rare vintage designer pleated skirt',
                'category': 'Bottoms',
                'price': Decimal('99.99'),
                'quantity': 1,
                'warranty_period': 0,
                'refurbishment_details': 'Professionally cleaned and restored',
                'thrift_condition_details': 'Minor wear, authentic vintage piece',
                'seller': sellers['vintage_vault'],
                'image': 'products/pleated_skirt.jpg'
            },
            {
                'product_name': 'Sustainable Denim Jacket',
                'product_type': 'Regular',
                'product_condition': 'New',
                'description': 'Eco-friendly denim jacket made from recycled materials',
                'category': 'Outerwear',
                'price': Decimal('89.99'),
                'quantity': 30,
                'warranty_period': 30,
                'seller': sellers['eco_fashion'],
                'image': 'products/denim_jacket.jpg'
            },
            {
                'product_name': 'Vintage Designer Bag',
                'product_type': 'Auction',
                'product_condition': 'Excellent',
                'description': 'Authentic vintage designer handbag, limited edition',
                'category': 'Accessories',
                'price': Decimal('299.99'),
                'quantity': 1,
                'warranty_period': 0,
                'refurbishment_details': 'Professional restoration',
                'thrift_condition_details': 'Excellent vintage condition',
                'seller': sellers['luxury_lane'],
                'image': 'products/designer_bag.jpg'
            },
            {
                'product_name': 'Eco-Friendly Sneakers',
                'product_type': 'Regular',
                'product_condition': 'New',
                'description': 'Sustainable sneakers made from recycled materials',
                'category': 'Footwear',
                'price': Decimal('69.99'),
                'quantity': 45,
                'warranty_period': 60,
                'seller': sellers['eco_fashion'],
                'image': 'products/eco_sneakers.jpg'
            }
        ]

        # Add products to database
        for product_data in clothing_products:
            seller = product_data.pop('seller')  # Remove seller from dict to avoid duplicate argument
            product = Product.objects.create(
                product_id=str(uuid.uuid4())[:8],
                seller=seller,
                **product_data
            )
            self.stdout.write(self.style.SUCCESS(f'Created product: {product.product_name} (Seller: {seller.seller_name})'))

        self.stdout.write(self.style.SUCCESS('Successfully populated database with clothing data')) 