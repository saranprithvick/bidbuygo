from django.core.management.base import BaseCommand
from django.db import connection
from bidbuygo.db_functions import create_database_objects

class Command(BaseCommand):
    help = 'Initialize database objects'

    def handle(self, *args, **options):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bidbuygo_bidding'")
                if cursor.fetchone():
                    create_database_objects()
                    self.stdout.write(self.style.SUCCESS('Successfully initialized database objects'))
                else:
                    self.stdout.write(self.style.WARNING('Bidding table does not exist yet. Please run migrations first.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error initializing database: {str(e)}')) 