from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured


class LDAPSettings(object):
    """Centralize defaults and validation for settings."""
    model = get_user_model()
    defaults = {
        'GROUP_FILTER': None,
        'GROUP_ATTRIBUTES': {},
        'USER_FILTER': None,
        'USER_ATTRIBUTES': {},
        'USER_EXTRA_ATTRIBUTES': [],
        'GROUPNAME_FIELD': 'name',
        'USERNAME_FIELD': getattr(model, 'USERNAME_FIELD', 'username'),
        'USER_CALLBACKS': [],
        'REMOVED_USER_CALLBACKS': [],
        'URI': '',
        'BASE_USER': '',
        'BASE_PASS': '',
        'BASE': '',
        'PAGE_SIZE': 100,
    }

    def __init__(self, prefix='LDAP_SYNC_'):
        """Load settings from Django configuration."""
        for name, default in self.defaults.items():
            value = getattr(settings, prefix + name, default)
            setattr(self, name, value)

        self.validate()

    def validate(self):
        """Apply validation rules for loaded settings."""
        if self.GROUP_ATTRIBUTES and self.GROUPNAME_FIELD not in self.GROUP_ATTRIBUTES.values():
            raise ImproperlyConfigured("LDAP_SYNC_GROUP_ATTRIBUTES must contain '%s'" % self.GROUPNAME_FIELD)

        if not self.model._meta.get_field(self.USERNAME_FIELD).unique:
            raise ImproperlyConfigured("LDAP_SYNC_USERNAME_FIELD '%s' must be unique" % self.USERNAME_FIELD)

        if self.USER_ATTRIBUTES and self.USERNAME_FIELD not in self.USER_ATTRIBUTES.values():
            raise ImproperlyConfigured("LDAP_SYNC_USER_ATTRIBUTES must contain '%s'" % self.USERNAME_FIELD)
