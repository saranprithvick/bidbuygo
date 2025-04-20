from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, Delivery

@receiver(post_save, sender=Order)
def create_delivery(sender, instance, created, **kwargs):
    """Create a delivery record when an order is created"""
    if created:
        Delivery.objects.create(
            order=instance,
            tracking_number=f'TRACK-{instance.order_id}',
            courier_service='Default Courier',
            status='pending'
        ) 