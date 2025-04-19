from django.apps import AppConfig


class BidbuygoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bidbuygo'

    def ready(self):
        from .db_functions import create_database_objects
        create_database_objects()
