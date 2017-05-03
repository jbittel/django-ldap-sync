import unittest

from django.test import override_settings
from django.test import TestCase

import ldap
from mockldap import MockLdap

from ldap_sync.sync import SyncLDAP


class SyncTests(TestCase):
    top = ('o=test', {'o': ['test']})
    example = ('ou=example,o=test', {'ou': ['example']})
    other = ('ou=other,o=test', {'ou': ['other']})
    manager = ('cn=manager,ou=example,o=test', {'cn': ['manager'], 'userPassword': ['ldaptest']})
    alice = ('cn=alice,ou=example,o=test', {'cn': ['alice'], 'userPassword': ['alicepw']})
    bob = ('cn=bob,ou=other,o=test', {'cn': ['bob'], 'userPassword': ['bobpw']})

    directory = dict([top, example, other, manager, alice, bob])

    @classmethod
    def setUpClass(cls):
        cls.mockldap = MockLdap(cls.directory)

    @classmethod
    def tearDownClass(cls):
        del cls.mockldap

    def setUp(self):
        self.mockldap.start()
        self.ldapobj = self.mockldap['ldap://localhost']
        self.sync = SyncLDAP()

    def tearDown(self):
        self.mockldap.stop()
        del self.ldapobj
        del self.sync

    def test_settings(self):
        """The settings property should allow access to configured settings."""
        self.assertEqual(self.sync.settings.BASE_USER, 'cn=alice,ou=example,o=test')
        self.assertEqual(self.sync.settings.BASE_PASS, 'alicepw')

    def test_ldap(self):
        """The ldap property should allow access to the LDAP connection."""
        results = self.sync.ldap.conn.search_s('ou=example,o=test', ldap.SCOPE_ONELEVEL, '(cn=*)')
        self.assertEquals(self.ldapobj.methods_called(), ['initialize', 'simple_bind_s', 'search_s'])
        self.assertEquals(sorted(results), sorted([self.manager, self.alice]))

    @override_settings(LDAP_SYNC_USER_FILTER='')
    def test_no_user_filter(self):
        """A user sync should not be performed if no filter is provided."""
        self.sync.sync_users()
        self.assertEqual(self.ldapobj.methods_called(), [])

    @override_settings(LDAP_SYNC_GROUP_FILTER='')
    def test_no_group_filter(self):
        """A group sync should not be performed if no filter is provided."""
        self.sync.sync_groups()
        self.assertEqual(self.ldapobj.methods_called(), [])
