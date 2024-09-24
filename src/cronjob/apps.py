from django.apps import AppConfig


class CronjobConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cronjob'

    def ready(self):
        # Import the signals to ensure they are registered
        import cronjob.signals