from django.apps import AppConfig


class ProspeccionConfig(AppConfig):
    name = 'prospeccion'

    def ready(self):
        from . import signals  # noqa: F401 — registra el receptor post_save de match automático
