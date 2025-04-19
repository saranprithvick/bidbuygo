import razorpay
from django.conf import settings
from .models import Transaction, Orders
import json

class PaymentManager:
    def __init__(self):
        self.client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    def create_order(self, amount, currency="INR"):
        """Create a Razorpay Order"""
        try:
            data = {
                "amount": int(amount * 100),  # Razorpay expects amount in paisa
                "currency": currency,
                "receipt": f"receipt_{str(amount)}",
                "payment_capture": 1  # Auto capture payment
            }
            order = self.client.order.create(data=data)
            return order
        except Exception as e:
            print(f"Error creating Razorpay order: {str(e)}")
            return None

    def verify_payment(self, razorpay_order_id, razorpay_payment_id, razorpay_signature):
        """Verify Razorpay payment signature"""
        try:
            return self.client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            })
        except Exception as e:
            print(f"Error verifying payment: {str(e)}")
            return False

    def process_payment(self, order_id, payment_details):
        """Process payment and update transaction status"""
        try:
            order = Orders.objects.get(order_id=order_id)
            
            # Create or update transaction
            transaction, created = Transaction.objects.get_or_create(
                order=order,
                defaults={
                    'transaction_amt': order.price_amt,
                    'payment_method': 'RAZORPAY',
                    'razorpay_order_id': payment_details.get('razorpay_order_id'),
                    'razorpay_payment_id': payment_details.get('razorpay_payment_id'),
                    'razorpay_signature': payment_details.get('razorpay_signature'),
                    'payment_status': 'COMPLETED' if payment_details.get('status') == 'success' else 'FAILED',
                    'mode_of_payment': 'Online'
                }
            )

            if not created:
                # Update existing transaction
                transaction.payment_status = 'COMPLETED' if payment_details.get('status') == 'success' else 'FAILED'
                transaction.razorpay_payment_id = payment_details.get('razorpay_payment_id')
                transaction.razorpay_signature = payment_details.get('razorpay_signature')
                transaction.save()

            # Update order status
            if payment_details.get('status') == 'success':
                order.order_status = 'PAID'
            else:
                order.order_status = 'PAYMENT_FAILED'
            order.save()

            return True, transaction
        except Exception as e:
            print(f"Error processing payment: {str(e)}")
            return False, None

    def initiate_refund(self, payment_id, amount=None):
        """Initiate refund for a payment"""
        try:
            if amount:
                refund_data = {
                    "amount": int(amount * 100),
                    "speed": "normal"
                }
            else:
                refund_data = {
                    "speed": "normal"
                }
            
            refund = self.client.payment.refund(payment_id, refund_data)
            return True, refund
        except Exception as e:
            print(f"Error initiating refund: {str(e)}")
            return False, None 