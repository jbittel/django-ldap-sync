from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.test.utils import override_settings

from ldap_sync.settings import SyncSettings


class SettingsTests(TestCase):
    def test_get_settings(self):
        """The settings object should contain all configured settings."""
        settings = SyncSettings()
        self.assertEqual(settings.URI, 'ldap://ldap.example.com:389')
        self.assertEqual(settings.BASE_USER, 'CN=Sync,CN=Users,DC=example,DC=com')
        self.assertEqual(settings.BASE_PASS, 'passw0rd')
        self.assertEqual(settings.BASE, 'DC=example,DC=com')
        self.assertEqual(settings.USER_FILTER, 'objectCategory=person')

    @override_settings(LDAP_SYNC_GROUP_ATTRIBUTES={'departmentName': 'department'})
    def test_validate_group_attributes(self):
        """Check the group attributes validation rule."""
        with self.assertRaises(ImproperlyConfigured):
            settings = SyncSettings()  # noqa

    @override_settings(LDAP_SYNC_USERNAME_FIELD='first_name')
    def test_validate_unique_username(self):
        """Check the unique username validation rule."""
        with self.assertRaises(ImproperlyConfigured):
            settings = SyncSettings()  # noqa

    @override_settings(LDAP_SYNC_USER_ATTRIBUTES={'givenName': 'first_name'})
    def test_validate_user_attributes(self):
        """Check the user attributes validation rule."""
        with self.assertRaises(ImproperlyConfigured):
            settings = SyncSettings()  # noqa
