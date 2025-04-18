from django.core.management.base import BaseCommand
from bidbuygo.models import Product, User, Seller
import uuid
from decimal import Decimal
from django.contrib.auth.hashers import make_password

class Command(BaseCommand):
    help = 'Populates the database with sample clothing data'

    def handle(self, *args, **kwargs):
        # Create a sample seller if not exists
        seller, created = Seller.objects.get_or_create(
            seller_name="FashionHub",
            email="fashionhub@example.com",
            mobile_number="1234567890",
            address="123 Fashion Street, Style City"
        )

        # Create a sample admin user if not exists
        admin_user, created = User.objects.get_or_create(
            user_name="admin",
            email="admin@example.com",
            defaults={
                'password': make_password('admin123'),
                'mobile_number': '9876543210',
                'address': 'Admin Address'
            }
        )

        # Sample clothing products
        clothing_products = [
            {
                'product_name': 'Classic White T-Shirt',
                'product_type': 'Thrift',
                'product_condition': 'Like New',
                'description': '100% cotton white t-shirt, perfect for everyday wear',
                'category': 'Tops',
                'price': Decimal('19.99'),
                'quantity': 50,
                'warranty_period': 0,
                'refurbishment_details': 'Gently used, professionally cleaned',
                'thrift_condition_details': 'No stains or tears, excellent condition'
            },
            {
                'product_name': 'Slim Fit Jeans',
                'product_type': 'Thrift',
                'product_condition': 'Good',
                'description': 'Blue denim jeans with slim fit design',
                'category': 'Bottoms',
                'price': Decimal('29.99'),
                'quantity': 30,
                'warranty_period': 0,
                'refurbishment_details': 'Lightly worn, professionally cleaned',
                'thrift_condition_details': 'Minor wear on knees, otherwise good condition'
            },
            {
                'product_name': 'Oversized Hoodie',
                'product_type': 'Thrift',
                'product_condition': 'Excellent',
                'description': 'Comfortable oversized hoodie perfect for casual wear',
                'category': 'Outerwear',
                'price': Decimal('39.99'),
                'quantity': 20,
                'warranty_period': 0,
                'refurbishment_details': 'Like new condition',
                'thrift_condition_details': 'No signs of wear, excellent condition'
            },
            {
                'product_name': 'Floral Summer Dress',
                'product_type': 'Thrift',
                'product_condition': 'Like New',
                'description': 'Beautiful floral print summer dress',
                'category': 'Dresses',
                'price': Decimal('34.99'),
                'quantity': 15,
                'warranty_period': 0,
                'refurbishment_details': 'Worn once, professionally cleaned',
                'thrift_condition_details': 'Perfect condition, no flaws'
            },
            {
                'product_name': 'Leather Jacket',
                'product_type': 'Thrift',
                'product_condition': 'Good',
                'description': 'Classic black leather jacket',
                'category': 'Outerwear',
                'price': Decimal('89.99'),
                'quantity': 10,
                'warranty_period': 0,
                'refurbishment_details': 'Gently used, professionally cleaned',
                'thrift_condition_details': 'Minor scuffs, otherwise good condition'
            },
            {
                'product_name': 'Striped Sweater',
                'product_type': 'Thrift',
                'product_condition': 'Excellent',
                'description': 'Warm striped sweater for winter',
                'category': 'Tops',
                'price': Decimal('24.99'),
                'quantity': 25,
                'warranty_period': 0,
                'refurbishment_details': 'Like new condition',
                'thrift_condition_details': 'No pilling or damage'
            },
            {
                'product_name': 'Pleated Skirt',
                'product_type': 'Thrift',
                'product_condition': 'Like New',
                'description': 'Elegant pleated midi skirt',
                'category': 'Bottoms',
                'price': Decimal('29.99'),
                'quantity': 18,
                'warranty_period': 0,
                'refurbishment_details': 'Worn once, professionally cleaned',
                'thrift_condition_details': 'Perfect condition'
            },
            {
                'product_name': 'Denim Jacket',
                'product_type': 'Thrift',
                'product_condition': 'Good',
                'description': 'Classic blue denim jacket',
                'category': 'Outerwear',
                'price': Decimal('44.99'),
                'quantity': 12,
                'warranty_period': 0,
                'refurbishment_details': 'Gently used, professionally cleaned',
                'thrift_condition_details': 'Minor fading, otherwise good condition'
            }
        ]

        # Add products to database
        for product_data in clothing_products:
            product = Product.objects.create(
                product_id=str(uuid.uuid4())[:8],
                seller=seller,
                **product_data
            )
            self.stdout.write(self.style.SUCCESS(f'Created product: {product.product_name}'))

        self.stdout.write(self.style.SUCCESS('Successfully populated database with clothing data')) 