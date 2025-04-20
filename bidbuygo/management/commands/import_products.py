from django.core.management.base import BaseCommand
from bidbuygo.models import Product
import json
import os
from django.core.files import File

class Command(BaseCommand):
    help = 'Import products from a JSON file'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the JSON file containing product data')
        parser.add_argument('--images-dir', type=str, help='Directory containing product images')

    def handle(self, *args, **options):
        json_file = options['json_file']
        images_dir = options.get('images_dir')

        if not os.path.exists(json_file):
            self.stdout.write(self.style.ERROR(f'JSON file {json_file} does not exist'))
            return

        with open(json_file, 'r') as f:
            products_data = json.load(f)

        for product_data in products_data:
            try:
                # Create or update product
                product, created = Product.objects.update_or_create(
                    product_id=product_data['product_id'],
                    defaults={
                        'name': product_data['name'],
                        'description': product_data['description'],
                        'price': product_data['price'],
                        'category': product_data['category'],
                        'brand': product_data['brand'],
                        'color': product_data['color'],
                        'material': product_data['material'],
                        'gender': product_data['gender'],
                        'is_active': product_data.get('is_active', True)
                    }
                )

                # Handle image if provided
                if images_dir and product_data.get('image'):
                    image_path = os.path.join(images_dir, product_data['image'])
                    if os.path.exists(image_path):
                        with open(image_path, 'rb') as img:
                            product.image.save(product_data['image'], File(img), save=True)

                status = 'Created' if created else 'Updated'
                self.stdout.write(self.style.SUCCESS(f'{status} product: {product.name}'))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing product {product_data.get("name")}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS('Product import completed')) 