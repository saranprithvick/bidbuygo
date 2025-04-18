from django.core.management.base import BaseCommand
from bidbuygo.models import Product, Seller
from django.core.files import File
import os
from django.conf import settings
import uuid
from PIL import Image
import io
import shutil

class Command(BaseCommand):
    help = 'Populates the database with sample products'

    def create_dummy_image(self, width=300, height=300, color=(255, 255, 255)):
        """Create a dummy image for testing"""
        img = Image.new('RGB', (width, height), color)
        img_io = io.BytesIO()
        img.save(img_io, format='JPEG')
        img_io.seek(0)
        return img_io

    def handle(self, *args, **kwargs):
        # Clean up existing products and images
        Product.objects.all().delete()
        products_dir = os.path.join(settings.MEDIA_ROOT, 'products')
        if os.path.exists(products_dir):
            shutil.rmtree(products_dir)
        os.makedirs(products_dir, exist_ok=True)

        # Create a sample seller first
        seller = Seller.objects.create(
            seller_id=str(uuid.uuid4())[:25],
            seller_name="Sample Seller"
        )

        # Sample products data - only clothing items
        products = [
            # Regular Products
            {
                'product_name': 'Classic White T-Shirt',
                'description': 'A comfortable and versatile white t-shirt for everyday wear.',
                'price': 499.00,
                'product_type': 'Regular',
                'product_condition': 'New',
                'quantity': 10,
                'category': 'Clothing',
                'image_path': 'products/white_tshirt.jpg'
            },
            {
                'product_name': 'Blue Jeans',
                'description': 'Classic blue denim jeans with a modern fit.',
                'price': 1299.00,
                'product_type': 'Regular',
                'product_condition': 'New',
                'quantity': 15,
                'category': 'Clothing',
                'image_path': 'products/blue_jeans.jpg'
            },
            {
                'product_name': 'Black Hoodie',
                'description': 'Warm and cozy black hoodie perfect for casual outings.',
                'price': 999.00,
                'product_type': 'Regular',
                'product_condition': 'New',
                'quantity': 8,
                'category': 'Clothing',
                'image_path': 'products/black_hoodie.jpg'
            },
            {
                'product_name': 'Striped Polo Shirt',
                'description': 'Classic striped polo shirt for a smart casual look.',
                'price': 799.00,
                'product_type': 'Regular',
                'product_condition': 'New',
                'quantity': 12,
                'category': 'Clothing',
                'image_path': 'products/striped_polo.jpg'
            },
            {
                'product_name': 'Chino Pants',
                'description': 'Versatile chino pants perfect for both casual and formal occasions.',
                'price': 1199.00,
                'product_type': 'Regular',
                'product_condition': 'New',
                'quantity': 10,
                'category': 'Clothing',
                'image_path': 'products/chino_pants.jpg'
            },
            # Thrift Products
            {
                'product_name': 'Vintage Denim Jacket',
                'description': 'Classic vintage denim jacket with unique wear patterns.',
                'price': 1499.00,
                'product_type': 'Thrift',
                'product_condition': 'Used',
                'quantity': 1,
                'category': 'Clothing',
                'image_path': 'products/vintage_jacket.jpg',
                'thrift_condition_details': 'Light wear on cuffs, authentic vintage piece'
            },
            {
                'product_name': 'Retro Sweater',
                'description': 'Vintage style sweater with unique pattern.',
                'price': 899.00,
                'product_type': 'Thrift',
                'product_condition': 'Used',
                'quantity': 1,
                'category': 'Clothing',
                'image_path': 'products/retro_sweater.jpg',
                'thrift_condition_details': 'Minor pilling, original 90s piece'
            },
            {
                'product_name': 'Vintage Flannel Shirt',
                'description': 'Classic plaid flannel shirt from the 90s.',
                'price': 699.00,
                'product_type': 'Thrift',
                'product_condition': 'Used',
                'quantity': 1,
                'category': 'Clothing',
                'image_path': 'products/vintage_flannel.jpg',
                'thrift_condition_details': 'Soft from years of wear, authentic vintage'
            },
            {
                'product_name': 'Retro Corduroy Pants',
                'description': 'Vintage corduroy pants with unique texture.',
                'price': 849.00,
                'product_type': 'Thrift',
                'product_condition': 'Used',
                'quantity': 1,
                'category': 'Clothing',
                'image_path': 'products/corduroy_pants.jpg',
                'thrift_condition_details': 'Light wear on knees, original 80s piece'
            },
            # Auction Products
            {
                'product_name': 'Designer Blazer',
                'description': 'Limited edition designer blazer in perfect condition.',
                'price': 4999.00,
                'product_type': 'Auction',
                'product_condition': 'New',
                'quantity': 1,
                'category': 'Clothing',
                'image_path': 'products/designer_blazer.jpg'
            },
            {
                'product_name': 'Vintage Leather Jacket',
                'description': 'Rare vintage leather jacket from the 80s.',
                'price': 7999.00,
                'product_type': 'Auction',
                'product_condition': 'Used',
                'quantity': 1,
                'category': 'Clothing',
                'image_path': 'products/vintage_leather.jpg'
            },
            {
                'product_name': 'Limited Edition Trench Coat',
                'description': 'Exclusive designer trench coat with unique detailing.',
                'price': 6499.00,
                'product_type': 'Auction',
                'product_condition': 'New',
                'quantity': 1,
                'category': 'Clothing',
                'image_path': 'products/trench_coat.jpg'
            },
            {
                'product_name': 'Designer Denim Jacket',
                'description': 'Limited edition designer denim jacket with unique embroidery and detailing.',
                'price': 3499.00,
                'product_type': 'Auction',
                'product_condition': 'New',
                'quantity': 1,
                'category': 'Clothing',
                'image_path': 'products/designer_denim.jpg'
            },
            {
                'product_name': 'Designer Cashmere Sweater',
                'description': 'Luxury cashmere sweater with intricate knit pattern.',
                'price': 4499.00,
                'product_type': 'Auction',
                'product_condition': 'New',
                'quantity': 1,
                'category': 'Clothing',
                'image_path': 'products/cashmere_sweater.jpg'
            }
        ]

        # Create sample products
        for product_data in products:
            # Create a dummy image
            img_io = self.create_dummy_image()
            
            # Create product with image
            product = Product.objects.create(
                product_id=str(uuid.uuid4())[:25],
                seller=seller,
                product_name=product_data['product_name'],
                product_type=product_data['product_type'],
                product_condition=product_data['product_condition'],
                description=product_data['description'],
                category=product_data['category'],
                price=product_data['price'],
                quantity=product_data['quantity'],
                is_available=True
            )

            # Save the image
            image_path = os.path.join(products_dir, os.path.basename(product_data['image_path']))
            with open(image_path, 'wb') as f:
                f.write(img_io.getvalue())
            
            # Update product with image path
            product.image = product_data['image_path']
            product.save()

            # Add thrift condition details if present
            if 'thrift_condition_details' in product_data:
                product.thrift_condition_details = product_data['thrift_condition_details']
                product.save()

        self.stdout.write(self.style.SUCCESS('Successfully populated database with sample products')) 