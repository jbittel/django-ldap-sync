import logging

import ldap
from ldap.ldapobject import LDAPObject
from ldap.controls import SimplePagedResultsControl

from django.conf import settings
from django.core.management.base import NoArgsCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ImproperlyConfigured
from django.db import IntegrityError


logger = logging.getLogger(__name__)


class Command(NoArgsCommand):
    help = "Synchronize users and groups from an authoritative LDAP server"

    def handle_noargs(self, **options):
        ldap_groups = self.get_ldap_groups()
        if ldap_groups:
            self.sync_ldap_groups(ldap_groups)

        ldap_users = self.get_ldap_users()
        if ldap_users:
            self.sync_ldap_users(ldap_users)

    def get_ldap_users(self):
        """
        Retrieve user data from target LDAP server.
        """
        user_filter = getattr(settings, 'LDAP_SYNC_USER_FILTER', None)
        if not user_filter:
            msg = "LDAP_SYNC_USER_FILTER not configured, skipping user sync"
            logger.info(msg)
            return None

        attributes = getattr(settings, 'LDAP_SYNC_USER_ATTRIBUTES', None)
        if not attributes:
            error_msg = ("LDAP_SYNC_USER_ATTRIBUTES must be specified in "
                         "your Django settings file")
            raise ImproperlyConfigured(error_msg)
        user_attributes = attributes.keys()

        users = self.ldap_search(user_filter, user_attributes)
        logger.debug("Retrieved %d users" % len(users))
        return users

    def sync_ldap_users(self, ldap_users):
        """
        Synchronize users with local user database.
        """
        model = get_user_model()
        attributes = getattr(settings, 'LDAP_SYNC_USER_ATTRIBUTES', None)
        username_field = getattr(model, 'USERNAME_FIELD', 'username')

        if username_field not in attributes.values():
            error_msg = ("LDAP_SYNC_USER_ATTRIBUTES must contain the "
                         "username field '%s'" % username_field)
            raise ImproperlyConfigured(error_msg)

        for cname, attrs in ldap_users:
            # In some cases with AD, attrs is a list instead of a
            # dict; these are not valid users, so skip them
            try:
                items = attrs.items()
            except AttributeError:
                continue

            # Extract user attributes from LDAP response
            user_attr = {}
            for name, attr in items:
                user_attr[attributes[name]] = attr[0].decode('utf-8')

            try:
                username = user_attr[username_field]
                user_attr[username_field] = username.lower()
            except KeyError:
                logger.warning("User is missing a required attribute '%s'" %
                               username_field)
                continue

            kwargs = {
                username_field + '__iexact': username,
                'defaults': user_attr,
            }

            # Create or update user data in the local database
            try:
                user, created = model.objects.get_or_create(**kwargs)
            except IntegrityError as e:
                logger.error("Error creating user %s: %s" % (username, e))
            else:
                updated_fields = []
                if created:
                    logger.debug("Created user %s" % username)
                    user.set_unusable_password()
                    updated_fields.append('password')
                else:
                    for name, attr in user_attr.items():
                        current_attr = getattr(user, name)
                        if current_attr != attr:
                            setattr(user, name, attr)
                            updated_fields.append(name)
                user.save(update_fields=updated_fields)

        logger.info("Users are synchronized")

    def get_ldap_groups(self):
        """
        Retrieve groups from target LDAP server.
        """
        group_filter = getattr(settings, 'LDAP_SYNC_GROUP_FILTER', None)
        if not group_filter:
            msg = "LDAP_SYNC_GROUP_FILTER not configured, skipping group sync"
            logger.info(msg)
            return None

        attributes = getattr(settings, 'LDAP_SYNC_GROUP_ATTRIBUTES', None)
        if not attributes:
            error_msg = ("LDAP_SYNC_GROUP_ATTRIBUTES must be specified in "
                         "your Django settings file")
            raise ImproperlyConfigured(error_msg)
        group_attributes = attributes.keys()

        groups = self.ldap_search(group_filter, group_attributes)
        logger.debug("Retrieved %d groups" % len(groups))
        return groups

    def sync_ldap_groups(self, ldap_groups):
        """
        Synchronize LDAP groups with local group database.
        """
        attributes = getattr(settings, 'LDAP_SYNC_GROUP_ATTRIBUTES', None)
        groupname_field = 'name'

        if groupname_field not in attributes.values():
            error_msg = ("LDAP_SYNC_GROUP_ATTRIBUTES must contain the "
                         "group name field '%s'" % groupname_field)
            raise ImproperlyConfigured(error_msg)

        for cname, attrs in ldap_groups:
            # In some cases with AD, attrs is a list instead of a
            # dict; these are not valid groups, so skip them
            try:
                items = attrs.items()
            except AttributeError:
                continue

            # Extract user data from LDAP response
            group_attr = {}
            for name, attr in items:
                group_attr[attributes[name]] = attr[0].decode('utf-8')

            try:
                groupname = group_attr[groupname_field]
                group_attr[groupname_field] = groupname.lower()
            except KeyError:
                logger.warning("Group is missing a required attribute '%s'" %
                               groupname_field)
                continue

            kwargs = {
                groupname_field + '__iexact': groupname,
                'defaults': group_attr,
            }

            # Create or update group data in the local database
            try:
                group, created = Group.objects.get_or_create(**kwargs)
            except IntegrityError as e:
                logger.error("Error creating group %s" % e)
            else:
                if created:
                    logger.debug("Created group %s" % groupname)

        logger.info("Groups are synchronized")

    def ldap_search(self, filter, attributes):
        """
        Query the configured LDAP server with the provided search
        filter and attribute list. Returns a list of the results
        returned.
        """
        uri = getattr(settings, 'LDAP_SYNC_URI', None)
        if not uri:
            error_msg = ("LDAP_SYNC_URI must be specified in your Django "
                         "settings file")
            raise ImproperlyConfigured(error_msg)

        base_user = getattr(settings, 'LDAP_SYNC_BASE_USER', None)
        if not base_user:
            error_msg = ("LDAP_SYNC_BASE_USER must be specified in your "
                         "Django settings file")
            raise ImproperlyConfigured(error_msg)

        base_pass = getattr(settings, 'LDAP_SYNC_BASE_PASS', None)
        if not base_pass:
            error_msg = ("LDAP_SYNC_BASE_PASS must be specified in your "
                         "Django settings file")
            raise ImproperlyConfigured(error_msg)

        base = getattr(settings, 'LDAP_SYNC_BASE', None)
        if not base:
            error_msg = ("LDAP_SYNC_BASE must be specified in your Django "
                         "settings file")
            raise ImproperlyConfigured(error_msg)

        ldap.set_option(ldap.OPT_REFERRALS, 0)
        l = PagedLDAPObject(uri)
        l.protocol_version = 3
        try:
            l.simple_bind_s(base_user, base_pass)
        except ldap.LDAPError:
            logger.error("Error connecting to LDAP server %s" % uri)
            raise

        results = l.paged_search_ext_s(base,
                                       ldap.SCOPE_SUBTREE,
                                       filter,
                                       attrlist=attributes,
                                       serverctrls=None)
        l.unbind_s()
        return results


class PagedResultsSearchObject:
    """
    Taken from the python-ldap paged_search_ext_s.py demo, showing how to use
    the paged results control: https://bitbucket.org/jaraco/python-ldap/
    """
    page_size = getattr(settings, 'LDAP_SYNC_PAGE_SIZE', 100)

    def paged_search_ext_s(self, base, scope, filterstr='(objectClass=*)',
                           attrlist=None, attrsonly=0, serverctrls=None,
                           clientctrls=None, timeout=-1, sizelimit=0):
        """
        Behaves exactly like LDAPObject.search_ext_s() but internally uses the
        simple paged results control to retrieve search results in chunks.
        """
        req_ctrl = SimplePagedResultsControl(True, size=self.page_size,
                                             cookie='')

        # Send first search request
        msgid = self.search_ext(base, ldap.SCOPE_SUBTREE, filterstr,
                                attrlist=attrlist,
                                serverctrls=(serverctrls or []) + [req_ctrl])
        results = []

        while True:
            rtype, rdata, rmsgid, rctrls = self.result3(msgid)
            results.extend(rdata)
            # Extract the simple paged results response control
            pctrls = [c for c in rctrls if c.controlType ==
                      SimplePagedResultsControl.controlType]

            if pctrls:
                if pctrls[0].cookie:
                    # Copy cookie from response control to request control
                    req_ctrl.cookie = pctrls[0].cookie
                    msgid = self.search_ext(base, ldap.SCOPE_SUBTREE,
                                            filterstr, attrlist=attrlist,
                                            serverctrls=(serverctrls or []) +
                                            [req_ctrl])
                else:
                    break

        return results


class PagedLDAPObject(LDAPObject, PagedResultsSearchObject):
    pass
