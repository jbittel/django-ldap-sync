from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def get_setting(name, default=None, strict=False):
    if strict and not hasattr(settings, name):
        raise ImproperlyConfigured("%s must be specified in your Django settings" % name)
    return getattr(settings, name, default)
