from django.apps import AppConfig


class CrosswalkConfig(AppConfig):
    name = 'crosswalk'

    def ready(self):
        from crosswalk import signals  # noqa
