from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules

class AutoConfig(AppConfig):
    name = 'auto'

    def ready(self):
        autodiscover_modules('auto')

