from django.apps import AppConfig


class FabzenAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fabzen_app'

    def ready(self):
        import fabzen_app.signals
