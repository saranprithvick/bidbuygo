from django.apps import AppConfig


class BidbuygoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bidbuygo'

    def ready(self):
        # Import signals here to avoid circular imports
        import bidbuygo.signals

        # Only create database objects if the tables exist
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bidbuygo_bidding'")
                if cursor.fetchone():
                    from .db_functions import create_database_objects
                    create_database_objects()
        except Exception:
            # If there's any error (like table doesn't exist), just pass
            pass
