from django.core.management.base import BaseCommand
from bidbuygo.services.bidding_service import BiddingService

class Command(BaseCommand):
    help = 'Checks and ends auctions that haven\'t received bids in 24 hours'

    def handle(self, *args, **options):
        try:
            BiddingService.check_and_end_auctions()
            self.stdout.write(self.style.SUCCESS('Successfully checked and ended auctions'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error checking auctions: {str(e)}')) 