from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.test.utils import override_settings

from ldap_sync.settings import LDAPSettings


class SettingsTests(TestCase):
    def test_get_settings(self):
        """The settings object should contain all configured settings."""
        settings = LDAPSettings()
        self.assertEqual(settings.URI, 'ldap://localhost')
        self.assertEqual(settings.BASE_USER, 'cn=alice,ou=example,o=test')
        self.assertEqual(settings.BASE_PASS, 'alicepw')
        self.assertEqual(settings.BASE, 'o=test')
        self.assertEqual(settings.USER_FILTER, 'objectCategory=person')

    @override_settings(LDAP_SYNC_GROUP_ATTRIBUTES={'departmentName': 'department'})
    def test_validate_group_attributes(self):
        """Check the group attributes validation rule."""
        with self.assertRaises(ImproperlyConfigured):
            settings = LDAPSettings()  # noqa

    @override_settings(LDAP_SYNC_USERNAME_FIELD='first_name')
    def test_validate_unique_username(self):
        """Check the unique username validation rule."""
        with self.assertRaises(ImproperlyConfigured):
            settings = LDAPSettings()  # noqa

    @override_settings(LDAP_SYNC_USER_ATTRIBUTES={'givenName': 'first_name'})
    def test_validate_user_attributes(self):
        """Check the user attributes validation rule."""
        with self.assertRaises(ImproperlyConfigured):
            settings = LDAPSettings()  # noqa
