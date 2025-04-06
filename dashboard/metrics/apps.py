# metrics/apps.py
from django.apps import AppConfig

class MetricsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'metrics'
    
    def ready(self):
        from . import scheduler
        scheduler.start()