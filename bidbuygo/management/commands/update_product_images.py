from django.core.management.base import BaseCommand
from bidbuygo.models import Product
import os

class Command(BaseCommand):
    help = 'Updates product images in the database'

    def handle(self, *args, **kwargs):
        # Map product names to image filenames
        product_images = {
            'Sustainable Denim Jacket': 'denim_jacket.jpg',
            'Vintage Designer Skirt': 'pleated_skirt.jpg',
            'Premium Leather Jacket': 'leather_jacket.jpg',
            'Eco-Friendly Sweater': 'striped_sweater.jpg',
            'Designer Oversized Hoodie': 'hoodie.jpg',
            'Vintage Floral Dress': 'floral_dress.jpg',
            'Vintage Slim Fit Jeans': 'slim_jeans.jpg',
            'Vintage Designer Bag': 'designer_bag.jpg',
            'Eco-Friendly Sneakers': 'eco_sneakers.jpg'
        }

        for product_name, image_filename in product_images.items():
            try:
                product = Product.objects.get(product_name=product_name)
                product.image = f'products/{image_filename}'
                product.save()
                self.stdout.write(self.style.SUCCESS(f'Updated image for {product_name}'))
            except Product.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Product {product_name} not found'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error updating {product_name}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS('Image update process completed')) 