from django.core.management.base import BaseCommand
from bidbuygo.models import Product, Category, Seller
from django.utils import timezone
from datetime import datetime, timedelta
import requests
from PIL import Image
import io
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
import uuid

class Command(BaseCommand):
    help = 'Populates the database with sample products'

    def handle(self, *args, **kwargs):
        # Create categories if they don't exist
        categories = {
            'Men': 'Men\'s clothing collection',
            'Women': 'Women\'s clothing collection'
        }
        
        for name, description in categories.items():
            Category.objects.get_or_create(
                name=name,
                defaults={'description': description}
            )

        # Create a default seller if none exists
        seller, _ = Seller.objects.get_or_create(
            seller_id='S001',
            defaults={'seller_name': 'Fashion Hub'}
        )

        # Sample products with unique images
        products = [
            # Men's Regular Products (10)
            {
                'product_name': 'Premium Cotton T-Shirt',
                'description': 'High-quality cotton t-shirt for everyday comfort',
                'price': 799,
                'product_type': 'Regular',
                'product_condition': 'New',
                'quantity': 50,
                'category': 'Men',
                'image_url': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab'
            },
            {
                'product_name': 'Slim Fit Denim Jeans',
                'description': 'Modern slim fit jeans with stretch comfort',
                'price': 1499,
                'product_type': 'Regular',
                'product_condition': 'New',
                'quantity': 30,
                'category': 'Men',
                'image_url': 'https://images.unsplash.com/photo-1542272604-787c3835535d'
            },
            {
                'product_name': 'Classic Oxford Shirt',
                'description': 'Timeless oxford shirt perfect for formal occasions',
                'price': 1299,
                'product_type': 'Regular',
                'product_condition': 'New',
                'quantity': 40,
                'category': 'Men',
                'image_url': 'https://images.unsplash.com/photo-1598033129183-c4f50c736f10'
            },
            {
                'product_name': 'Casual Blazer',
                'description': 'Versatile blazer for both casual and semi-formal wear',
                'price': 2999,
                'product_type': 'Regular',
                'product_condition': 'New',
                'quantity': 20,
                'category': 'Men',
                'image_url': 'https://images.unsplash.com/photo-1507679799987-c73779587ccf'
            },
            {
                'product_name': 'Wool Sweater',
                'description': 'Warm wool sweater for winter season',
                'price': 1899,
                'product_type': 'Regular',
                'product_condition': 'New',
                'quantity': 25,
                'category': 'Men',
                'image_url': 'https://images.unsplash.com/photo-1578587018452-892bacefd3f2'
            },
            {
                'product_name': 'Polo Shirt',
                'description': 'Classic polo shirt for a smart casual look',
                'price': 899,
                'product_type': 'Regular',
                'product_condition': 'New',
                'quantity': 45,
                'category': 'Men',
                'image_url': 'https://images.unsplash.com/photo-1586363104862-3a5e2ab60d99'
            },
            {
                'product_name': 'Chino Pants',
                'description': 'Comfortable chino pants for everyday wear',
                'price': 1299,
                'product_type': 'Regular',
                'product_condition': 'New',
                'quantity': 35,
                'category': 'Men',
                'image_url': 'https://images.unsplash.com/photo-1473966968600-fa801b869a1a'
            },
            {
                'product_name': 'Leather Jacket',
                'description': 'Premium leather jacket for a bold look',
                'price': 4999,
                'product_type': 'Regular',
                'product_condition': 'New',
                'quantity': 15,
                'category': 'Men',
                'image_url': 'https://images.unsplash.com/photo-1520975954732-35dd22299614'
            },
            {
                'product_name': 'Formal Suit',
                'description': 'Two-piece formal suit for special occasions',
                'price': 7999,
                'product_type': 'Regular',
                'product_condition': 'New',
                'quantity': 10,
                'category': 'Men',
                'image_url': 'https://images.unsplash.com/photo-1617127365659-c47fa864d8bc'
            },
            {
                'product_name': 'Hooded Sweatshirt',
                'description': 'Comfortable hoodie for casual wear',
                'price': 1599,
                'product_type': 'Regular',
                'product_condition': 'New',
                'quantity': 30,
                'category': 'Men',
                'image_url': 'https://images.unsplash.com/photo-1556821840-3a63f95609a7'
            },

            # Women's Regular Products (5)
            {
                'product_name': 'Designer Dress',
                'description': 'Elegant designer dress for special occasions',
                'price': 2999,
                'product_type': 'Regular',
                'product_condition': 'New',
                'quantity': 20,
                'category': 'Women',
                'image_url': 'https://images.unsplash.com/photo-1572804013309-59a88b7e92f1'
            },
            {
                'product_name': 'Silk Blouse',
                'description': 'Premium silk blouse for a sophisticated look',
                'price': 1799,
                'product_type': 'Regular',
                'product_condition': 'New',
                'quantity': 25,
                'category': 'Women',
                'image_url': 'https://images.unsplash.com/photo-1554568218-0f1715e72254'
            },
            {
                'product_name': 'High-Waist Jeans',
                'description': 'Trendy high-waist jeans with perfect fit',
                'price': 1699,
                'product_type': 'Regular',
                'product_condition': 'New',
                'quantity': 30,
                'category': 'Women',
                'image_url': 'https://images.unsplash.com/photo-1541099649105-f69ad21f3246'
            },
            {
                'product_name': 'Summer Maxi Dress',
                'description': 'Flowing maxi dress perfect for summer',
                'price': 2299,
                'product_type': 'Regular',
                'product_condition': 'New',
                'quantity': 20,
                'category': 'Women',
                'image_url': 'https://images.unsplash.com/photo-1585487000160-6ebcfceb0d03'
            },
            {
                'product_name': 'Cashmere Sweater',
                'description': 'Luxurious cashmere sweater for winter',
                'price': 3499,
                'product_type': 'Regular',
                'product_condition': 'New',
                'quantity': 15,
                'category': 'Women',
                'image_url': 'https://images.unsplash.com/photo-1576566588028-4147f3842f27'
            },

            # Thrift Products (10)
            {
                'product_name': 'Vintage Levi\'s Denim Jacket',
                'description': 'Authentic vintage Levi\'s jacket, excellent condition',
                'price': 2499,
                'product_type': 'Thrift',
                'product_condition': 'Used',
                'quantity': 1,
                'category': 'Men',
                'image_url': 'https://images.unsplash.com/photo-1591047139829-d91aecb6caea'
            },
            {
                'product_name': 'Pre-owned Designer Suit',
                'description': 'Gently used designer suit, perfect condition',
                'price': 3999,
                'product_type': 'Thrift',
                'product_condition': 'Used',
                'quantity': 1,
                'category': 'Men',
                'image_url': 'https://images.unsplash.com/photo-1594938298603-c8148c4dae35'
            },
            {
                'product_name': 'Vintage Leather Boots',
                'description': 'Classic leather boots, well maintained',
                'price': 1999,
                'product_type': 'Thrift',
                'product_condition': 'Used',
                'quantity': 1,
                'category': 'Men',
                'image_url': 'https://images.unsplash.com/photo-1638247025967-b4e38f787b76'
            },
            {
                'product_name': 'Designer Evening Gown',
                'description': 'Elegant pre-owned evening gown, mint condition',
                'price': 3499,
                'product_type': 'Thrift',
                'product_condition': 'Used',
                'quantity': 1,
                'category': 'Women',
                'image_url': 'https://images.unsplash.com/photo-1566174053879-31528523f8ae'
            },
            {
                'product_name': 'Vintage Chanel Bag',
                'description': 'Authentic vintage Chanel handbag, good condition',
                'price': 4999,
                'product_type': 'Thrift',
                'product_condition': 'Used',
                'quantity': 1,
                'category': 'Women',
                'image_url': 'https://images.unsplash.com/photo-1548036328-c9fa89d128fa'
            },
            {
                'product_name': 'Classic Wool Coat',
                'description': 'Vintage wool coat, excellent condition',
                'price': 2799,
                'product_type': 'Thrift',
                'product_condition': 'Used',
                'quantity': 1,
                'category': 'Men',
                'image_url': 'https://images.unsplash.com/photo-1544923246-77307dd654cb'
            },
            {
                'product_name': 'Vintage Designer Blazer',
                'description': 'Premium designer blazer, well preserved',
                'price': 2299,
                'product_type': 'Thrift',
                'product_condition': 'Used',
                'quantity': 1,
                'category': 'Women',
                'image_url': 'https://images.unsplash.com/photo-1591369822096-ffd140ec948f'
            },
            {
                'product_name': 'Retro Denim Collection',
                'description': 'Curated vintage denim pieces, great condition',
                'price': 1899,
                'product_type': 'Thrift',
                'product_condition': 'Used',
                'quantity': 1,
                'category': 'Men',
                'image_url': 'https://images.unsplash.com/photo-1582552938357-32b906df40cb'
            },
            {
                'product_name': 'Vintage Silk Scarf Collection',
                'description': 'Collection of premium silk scarves, excellent condition',
                'price': 999,
                'product_type': 'Thrift',
                'product_condition': 'Used',
                'quantity': 1,
                'category': 'Women',
                'image_url': 'https://images.unsplash.com/photo-1584030373081-f37b7bb4fa8e'
            }
        ]

        for product_data in products:
            try:
                # Generate a unique product_id
                product_id = f"P{str(uuid.uuid4())[:8]}"
                
                # Download and save the image
                response = requests.get(product_data['image_url'])
                if response.status_code == 200:
                    img_temp = NamedTemporaryFile(delete=True)
                    img_temp.write(response.content)
                    img_temp.flush()
                    
                    # Get or create category
                    category = Category.objects.get(name=product_data['category'])
                    
                    # Create product
                    product = Product.objects.create(
                        product_id=product_id,
                        product_name=product_data['product_name'],
                        description=product_data['description'],
                        price=product_data['price'],
                        product_type=product_data['product_type'],
                        product_condition=product_data['product_condition'],
                        quantity=product_data['quantity'],
                        category=category,
                        seller=seller
                    )
                    
                    # Save the image
                    product.image.save(
                        f"{product.product_name.lower().replace(' ', '_')}.jpg",
                        File(img_temp),
                        save=True
                    )
                    
                    self.stdout.write(self.style.SUCCESS(f'Successfully created product: {product.product_name}'))
                else:
                    self.stdout.write(self.style.ERROR(f'Failed to download image for {product_data["product_name"]}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating product {product_data["product_name"]}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS('Successfully populated database with products')) 