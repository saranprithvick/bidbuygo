from django.utils import timezone
from decimal import Decimal
from .models import Product, Bidding, User
from django.db import transaction
from django.core.exceptions import ValidationError

class BiddingService:
    @staticmethod
    def place_bid(user: User, product: Product, bid_amount: Decimal, is_auto_bid: bool = False, 
                 auto_bid_limit: Decimal = None, bid_increment: Decimal = Decimal('1.00')) -> Bidding:
        """
        Place a bid on an auction product
        
        Args:
            user: The user placing the bid
            product: The product being bid on
            bid_amount: The amount of the bid
            is_auto_bid: Whether this is an auto-bid
            auto_bid_limit: Maximum amount for auto-bidding
            bid_increment: Amount to increment bids by
            
        Returns:
            Bidding: The created bid object
            
        Raises:
            ValidationError: If the bid is invalid
        """
        if product.product_type != 'Auction':
            raise ValidationError("Bidding is only allowed on auction products")
            
        if product.auction_end_date and product.auction_end_date < timezone.now().date():
            raise ValidationError("Auction has ended")
            
        if bid_amount <= product.current_bid if product.current_bid else product.price:
            raise ValidationError("Bid amount must be higher than current bid")
            
        if is_auto_bid and auto_bid_limit and bid_amount > auto_bid_limit:
            raise ValidationError("Auto-bid amount cannot exceed auto-bid limit")
            
        with transaction.atomic():
            # Create the bid
            bid = Bidding.objects.create(
                user=user,
                product=product,
                bid_amt=bid_amount,
                is_auto_bid=is_auto_bid,
                auto_bid_limit=auto_bid_limit,
                bid_increment=bid_increment,
                initial_bid_amt=bid_amount,
                auction_end_time=product.auction_end_date
            )
            
            # Update product's current bid
            product.current_bid = bid_amount
            product.save()
            
            # Process auto-bids if needed
            if is_auto_bid:
                BiddingService._process_auto_bids(product, bid)
                
        return bid
        
    @staticmethod
    def _process_auto_bids(product: Product, current_bid: Bidding):
        """
        Process auto-bids for a product when a new bid is placed
        
        Args:
            product: The product being bid on
            current_bid: The current highest bid
        """
        # Get all active auto-bids for this product
        auto_bids = Bidding.objects.filter(
            product=product,
            is_auto_bid=True,
            auto_bid_limit__gt=current_bid.bid_amt,
            bid_status='Pending'
        ).exclude(user=current_bid.user).order_by('bid_time')
        
        for auto_bid in auto_bids:
            # Calculate next bid amount
            next_bid = current_bid.bid_amt + auto_bid.bid_increment
            
            if next_bid <= auto_bid.auto_bid_limit:
                # Place the auto-bid
                BiddingService.place_bid(
                    user=auto_bid.user,
                    product=product,
                    bid_amount=next_bid,
                    is_auto_bid=True,
                    auto_bid_limit=auto_bid.auto_bid_limit,
                    bid_increment=auto_bid.bid_increment
                )
                break
                
    @staticmethod
    def end_auction(product: Product):
        """
        End an auction and determine the winner
        
        Args:
            product: The product whose auction is ending
        """
        if product.product_type != 'Auction':
            raise ValidationError("Only auction products can be ended")
            
        with transaction.atomic():
            # Get the highest bid
            highest_bid = Bidding.objects.filter(
                product=product,
                bid_status='Pending'
            ).order_by('-bid_amt').first()
            
            if highest_bid:
                # Mark the winner
                highest_bid.bid_status = 'Won'
                highest_bid.is_winner = True
                highest_bid.save()
                
                # Mark other bids as lost
                Bidding.objects.filter(
                    product=product,
                    bid_status='Pending'
                ).exclude(id=highest_bid.id).update(bid_status='Lost')
                
                # Update product status
                product.is_available = False
                product.save()
                
    @staticmethod
    def get_auction_status(product: Product):
        """
        Get the current status of an auction
        
        Args:
            product: The product to check
            
        Returns:
            dict: Auction status information
        """
        if product.product_type != 'Auction':
            raise ValidationError("Only auction products have auction status")
            
        current_bid = Bidding.objects.filter(
            product=product,
            bid_status='Pending'
        ).order_by('-bid_amt').first()
        
        return {
            'current_bid': current_bid.bid_amt if current_bid else product.price,
            'time_remaining': product.auction_end_date - timezone.now().date() if product.auction_end_date else None,
            'bid_count': Bidding.objects.filter(product=product).count(),
            'highest_bidder': current_bid.user if current_bid else None,
            'has_ended': product.auction_status == 'Ended' if hasattr(product, 'auction_status') else False
        } 