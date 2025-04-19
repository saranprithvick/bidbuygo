from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError
from decimal import Decimal
from ..models import Product, Bidding
from datetime import timedelta

class BiddingService:
    @staticmethod
    def place_bid(user, product, bid_amount, auto_bid_limit=None):
        """
        Place a bid on a product
        """
        with transaction.atomic():
            # Validate product is available for bidding
            if product.product_type != 'Auction':
                raise ValidationError("This product is not available for auction")
            
            # Check if auction has already ended
            if product.auction_status == 'Ended':
                raise ValidationError("This auction has already ended")

            # Get current highest bid
            current_highest_bid = Bidding.objects.filter(
                product=product,
                bid_status='Pending'
            ).order_by('-bid_amt').first()

            # Validate bid amount
            min_bid = product.current_bid or product.price
            if current_highest_bid:
                min_bid = current_highest_bid.bid_amt + Decimal('1.00')  # Minimum increment

            if bid_amount < min_bid:
                raise ValidationError(f"Bid must be at least {min_bid}")

            # Create new bid
            bid = Bidding.objects.create(
                user=user,
                product=product,
                bid_amt=bid_amount,
                initial_bid_amt=min_bid,
                is_auto_bid=bool(auto_bid_limit),
                auto_bid_limit=auto_bid_limit,
                bid_status='Pending',
                bid_time=timezone.now()
            )

            # Update product's current bid and last bid time
            product.current_bid = bid_amount
            product.last_bid_time = timezone.now()
            product.save()

            # If auto-bidding is enabled, process auto-bids
            if auto_bid_limit:
                BiddingService._process_auto_bids(product)

            return bid

    @staticmethod
    def _process_auto_bids(product):
        """
        Process auto-bids for a product
        """
        auto_bids = Bidding.objects.filter(
            product=product,
            is_auto_bid=True,
            bid_status='Pending'
        ).exclude(
            auto_bid_limit__lte=product.current_bid
        ).order_by('-auto_bid_limit', 'bid_time')

        if len(auto_bids) < 2:
            return

        # Get the two highest auto-bids
        highest_auto_bid = auto_bids[0]
        second_highest_auto_bid = auto_bids[1]

        # Calculate the winning bid amount
        winning_bid_amount = min(
            second_highest_auto_bid.auto_bid_limit + Decimal('1.00'),
            highest_auto_bid.auto_bid_limit
        )

        # Create new bid for the winner
        Bidding.objects.create(
            user=highest_auto_bid.user,
            product=product,
            bid_amt=winning_bid_amount,
            initial_bid_amt=product.current_bid,
            is_auto_bid=True,
            auto_bid_limit=highest_auto_bid.auto_bid_limit,
            bid_status='Pending',
            bid_time=timezone.now()
        )

        # Update product's current bid and last bid time
        product.current_bid = winning_bid_amount
        product.last_bid_time = timezone.now()
        product.save()

    @staticmethod
    def check_and_end_auctions():
        """
        Check all active auctions and end those that haven't received bids in 24 hours
        """
        now = timezone.now()
        active_auctions = Product.objects.filter(
            product_type='Auction',
            auction_status='Active'
        )

        for product in active_auctions:
            if product.last_bid_time and (now - product.last_bid_time) > timedelta(hours=24):
                BiddingService.end_auction(product)

    @staticmethod
    def end_auction(product):
        """
        End an auction and determine the winner
        """
        with transaction.atomic():
            if product.product_type != 'Auction':
                raise ValidationError("This product is not an auction item")

            # Get the highest bid
            winning_bid = Bidding.objects.filter(
                product=product,
                bid_status='Pending'
            ).order_by('-bid_amt').first()

            if winning_bid:
                # Mark the winning bid
                winning_bid.bid_status = 'Won'
                winning_bid.is_winner = True
                winning_bid.save()

                # Mark all other bids as lost
                Bidding.objects.filter(
                    product=product,
                    bid_status='Pending'
                ).exclude(id=winning_bid.id).update(
                    bid_status='Lost'
                )

            # Update product status
            product.auction_status = 'Ended'
            product.save()

            return winning_bid

    @staticmethod
    def get_auction_status(product):
        """
        Get the current status of an auction
        """
        if product.product_type != 'Auction':
            return {
                'is_auction': False
            }

        current_highest_bid = Bidding.objects.filter(
            product=product,
            bid_status='Pending'
        ).order_by('-bid_amt').first()

        total_bids = Bidding.objects.filter(
            product=product
        ).count()

        # Calculate time remaining
        time_remaining = None
        if product.last_bid_time:
            time_elapsed = timezone.now() - product.last_bid_time
            time_remaining = max(0, 24 - time_elapsed.total_seconds() / 3600)  # Convert to hours

        return {
            'is_auction': True,
            'current_bid': product.current_bid or product.price,
            'highest_bidder': current_highest_bid.user if current_highest_bid else None,
            'total_bids': total_bids,
            'time_remaining': f"{time_remaining:.1f} hours" if time_remaining else "No bids yet",
            'auction_status': product.auction_status,
            'last_bid_time': product.last_bid_time,
            'has_ended': product.auction_status == 'Ended'
        } 