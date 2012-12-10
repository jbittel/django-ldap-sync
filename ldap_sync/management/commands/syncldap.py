import ldap
from ldap.ldapobject import LDAPObject
from ldap.controls import SimplePagedResultsControl
import logging

from django.conf import settings
from django.core.management.base import NoArgsCommand
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.models import SiteProfileNotAvailable
from django.core.exceptions import ImproperlyConfigured


log = logging.getLogger(__name__)


class Command(NoArgsCommand):
    help = "Synchronize users and groups with an authoritative LDAP server"

    def handle_noargs(self, **options):
        ldap_groups = self.get_ldap_groups()
        ldap_users = self.get_ldap_users()

        self.sync_ldap_groups(ldap_groups)
        self.sync_ldap_users(ldap_users, ldap_groups)

    def get_ldap_users(self):
        """
        Retrieve user data from target LDAP server.
        """
        user_filter = getattr(settings, 'LDAP_SYNC_USER_FILTER', None)
        if not user_filter:
            raise ImproperlyConfigured("LDAP_SYNC_USER_FILTER must be "
                "specified in your Django settings file")

        attributes = getattr(settings, 'LDAP_SYNC_USER_ATTRIBUTES', None)
        if not attributes:
            raise ImproperlyConfigured("LDAP_SYNC_USER_ATTRIBUTES must be "
                "specified in your Django settings file")
        user_attributes = attributes.keys()

        ldap.set_option(ldap.OPT_REFERRALS, 0)
        l = PagedLDAPObject(settings.LDAP_SYNC_URI)
        l.protocol_version = 3
        l.simple_bind_s(settings.LDAP_SYNC_BASE_USER,
            settings.LDAP_SYNC_BASE_PASS)
        l.page_size = getattr(settings, 'LDAP_SYNC_PAGE_SIZE', 100)

        users = l.paged_search_ext_s(
            settings.LDAP_SYNC_BASE,
            ldap.SCOPE_SUBTREE,
            user_filter,
            attrlist=user_attributes,
            serverctrls=None
        )

        l.unbind_s()

        log.debug("Received %d users" % len(users))
        return users

    def sync_ldap_users(self, ldap_users, ldap_groups):
        """
        Synchronize users with local user database.
        """
        for ldap_user in ldap_users:
            # Extract user data from LDAP response
            user_data = {}
            for (name, attr) in ldap_user[1].items():
                user_data[settings.LDAP_SYNC_USER_ATTRIBUTES[name]] = attr[0]

            # Create filter attribute dict from config and response
            filter_attr = getattr(settings, 'LDAP_SYNC_FILTER_ATTRIBUTES', None)
            if not filter_attr:
                raise ImproperlyConfigured("LDAP_SYNC_FILTER_ATTRIBUTES must be "
                    "specified in your Django settings file")

            # Build filter dictionary from specified filter attributes
            user_filter = {}
            for attr in filter_attr:
                try:
                    user_filter[attr] = user_data[attr]
                except KeyError:
                    pass

            # If no filter data was found, skip the user
            if not user_filter:
                continue

            # Create or update user data in local database
            user = User.objects.filter(**user_filter).update(**user_data)
            if not user:
                user_data.update(user_filter)
                user = User.objects.create(**user_data)
                log.debug("Created user %s" % user.username)

        log.info("Users are synchronized")

    def get_ldap_groups(self):
        """
        Retrieve groups from target LDAP server.
        """
        group_filter = getattr(settings, 'LDAP_SYNC_GROUP_FILTER', None)
        if not group_filter:
            raise ImproperlyConfigured("LDAP_SYNC_GROUP_FILTER must be "
                "specified in your Django settings file")

        attributes = getattr(settings, 'LDAP_SYNC_GROUP_ATTRIBUTES', None)
        if not attributes:
            raise ImproperlyConfigured("LDAP_SYNC_GROUP_ATTRIBUTES must be "
                "specified in your Django settings file")
        group_attributes = attributes.keys()

        ldap.set_option(ldap.OPT_REFERRALS, 0)
        l = PagedLDAPObject(settings.LDAP_SYNC_URI)
        l.protocol_version = 3
        l.simple_bind_s(settings.LDAP_SYNC_BASE_USER,
            settings.LDAP_SYNC_BASE_PASS)
        l.page_size = getattr(settings, 'LDAP_SYNC_PAGE_SIZE', 100)

        groups = l.paged_search_ext_s(
            settings.LDAP_SYNC_BASE,
            ldap.SCOPE_SUBTREE,
            group_filter,
            attrlist=group_attributes,
            serverctrls=None
        )

        l.unbind_s()

        log.debug("Received %d groups" % len(groups))
        return groups

    def sync_ldap_groups(self, ldap_groups):
        """
        Synchronize groups with local group database.
        """
        for ldap_group in ldap_groups:
            # Extract user data from LDAP response
            group_data = {}
            for (name, attr) in ldap_group[1].items():
                group_data[settings.LDAP_SYNC_GROUP_ATTRIBUTES[name]] = attr[0]

            try:
                group = Group.objects.get(**group_data)
            except Group.DoesNotExist:
                group = Group(**group_data)
                group.save()
                log.debug("Created group %s" % group.name)

        log.info("Groups are synchronized")


class PagedResultsSearchObject:
    """
    Taken from the python-ldap paged_search_ext_s.py demo, showing how to use
    the paged results control:

    https://bitbucket.org/jaraco/python-ldap/src/f208b6338a28/Demo/paged_search_ext_s.py
    """
    page_size = 50

    def paged_search_ext_s(self, base, scope, filterstr='(objectClass=*)',
        attrlist=None, attrsonly=0, serverctrls=None, clientctrls=None,
        timeout=-1, sizelimit=0):
        """
        Behaves exactly like LDAPObject.search_ext_s() but internally uses the
        simple paged results control to retrieve search results in chunks.
        """
        req_ctrl = SimplePagedResultsControl(True, size=self.page_size,
            cookie='')

        # Send first search request
        msgid = self.search_ext(
            base,
            ldap.SCOPE_SUBTREE,
            filterstr,
            attrlist=attrlist,
            serverctrls=(serverctrls or [])+[req_ctrl]
        )

        results = []

        while True:
            rtype, rdata, rmsgid, rctrls = self.result3(msgid)
            results.extend(rdata)
            # Extract the simple paged results response control
            pctrls = [ c for c in rctrls
                if c.controlType == SimplePagedResultsControl.controlType
            ]

            if pctrls:
                if pctrls[0].cookie:
                    # Copy cookie from response control to request control
                    req_ctrl.cookie = pctrls[0].cookie
                    msgid = self.search_ext(
                        base,
                        ldap.SCOPE_SUBTREE,
                        filterstr,
                        attrlist=attrlist,
                        serverctrls=(serverctrls or [])+[req_ctrl]
                    )
                else:
                    break

        return results

class PagedLDAPObject(LDAPObject,PagedResultsSearchObject):
    pass
