from django.core.management.base import BaseCommand
from bidbuygo.db_functions import create_database_objects

class Command(BaseCommand):
    help = 'Creates database functions, triggers, and procedures'

    def handle(self, *args, **options):
        try:
            create_database_objects()
            self.stdout.write(self.style.SUCCESS('Successfully created database objects'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating database objects: {str(e)}')) 