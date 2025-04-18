from django.core.management.base import BaseCommand
import requests
import os
from bidbuygo.models import Product
from django.conf import settings

class Command(BaseCommand):
    help = 'Downloads and saves product images'

    def handle(self, *args, **kwargs):
        # Create media/products directory if it doesn't exist
        media_dir = os.path.join(settings.MEDIA_ROOT, 'products')
        os.makedirs(media_dir, exist_ok=True)

        # Real product images URLs from Google
        product_images = {
            'denim_jacket.jpg': 'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?q=80&w=1000',
            'pleated_skirt.jpg': 'https://images.unsplash.com/photo-1584370848010-d7fe6bc767ec?q=80&w=1000',
            'leather_jacket.jpg': 'https://images.unsplash.com/photo-1551028719-00167b16eac5?q=80&w=1000',
            'striped_sweater.jpg': 'https://images.unsplash.com/photo-1611312449408-fcece27cdbb7?q=80&w=1000',
            'hoodie.jpg': 'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?q=80&w=1000',
            'floral_dress.jpg': 'https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?q=80&w=1000',
            'slim_jeans.jpg': 'https://images.unsplash.com/photo-1542272604-787c3835535d?q=80&w=1000',
            'designer_bag.jpg': 'https://images.unsplash.com/photo-1584917865442-de89df76afd3?q=80&w=1000',
            'eco_sneakers.jpg': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=1000'
        }

        for filename, url in product_images.items():
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    file_path = os.path.join(media_dir, filename)
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    self.stdout.write(self.style.SUCCESS(f'Successfully downloaded {filename}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Failed to download {filename}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error downloading {filename}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS('Image download process completed')) 