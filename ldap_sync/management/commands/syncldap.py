import logging

import ldap
from ldap.ldapobject import LDAPObject
from ldap.controls import SimplePagedResultsControl

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import DataError
from django.db import IntegrityError
from django.utils.module_loading import import_string

from ldap_sync.utils import get_setting


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    can_import_settings = True
    help = 'Synchronize users and groups from an authoritative LDAP server'

    def handle(self, *args, **options):
        ldap_groups = self.get_ldap_groups()
        if ldap_groups:
            self.sync_ldap_groups(ldap_groups)

        ldap_users = self.get_ldap_users()
        if ldap_users:
            self.sync_ldap_users(ldap_users)

    def get_ldap_users(self):
        """Retrieve user data from LDAP server."""
        user_filter = get_setting('LDAP_SYNC_USER_FILTER')
        if not user_filter:
            logger.debug('LDAP_SYNC_USER_FILTER not configured, skipping user sync')
            return None

        user_attributes = get_setting('LDAP_SYNC_USER_ATTRIBUTES', strict=True)
        user_keys = set(user_attributes.keys())
        user_extra_attributes = get_setting('LDAP_SYNC_USER_EXTRA_ATTRIBUTES', default=[])
        user_keys.update(user_extra_attributes)

        users = self.ldap_search(user_filter, user_keys)
        logger.debug("Retrieved %d users" % len(users))
        return users

    def sync_ldap_users(self, ldap_users):
        """Synchronize users with local user model."""
        model = get_user_model()
        user_attributes = get_setting('LDAP_SYNC_USER_ATTRIBUTES')
        username_field = get_setting('LDAP_SYNC_USERNAME_FIELD')
        if username_field is None:
            username_field = getattr(model, 'USERNAME_FIELD', 'username')
        user_callbacks = list(get_setting('LDAP_SYNC_USER_CALLBACKS', default=[]))
        removed_user_callbacks = list(get_setting('LDAP_SYNC_REMOVED_USER_CALLBACKS', default=[]))
        ldap_usernames = set()

        if not model._meta.get_field(username_field).unique:
            raise ImproperlyConfigured("Field '%s' must be unique" % username_field)

        if username_field not in user_attributes.values():
            error_msg = ("LDAP_SYNC_USER_ATTRIBUTES must contain the field '%s'" % username_field)
            raise ImproperlyConfigured(error_msg)

        for cname, attributes in ldap_users:
            defaults = {}
            try:
                for name, attribute in attributes.items():
                    try:
                        defaults[user_attributes[name]] = attribute[0].decode('utf-8')
                    except KeyError:
                        pass
            except AttributeError:
                # In some cases attributes is a list instead of a dict; skip these invalid users
                continue

            try:
                username = defaults[username_field].lower()
            except KeyError:
                logger.warning("User is missing a required attribute '%s'" % username_field)
                continue

            kwargs = {
                username_field + '__iexact': username,
                'defaults': defaults,
            }

            try:
                user, created = model.objects.get_or_create(**kwargs)
            except (IntegrityError, DataError) as e:
                logger.error("Error creating user %s: %s" % (username, e))
            else:
                updated = False
                if created:
                    logger.debug("Created user %s" % username)
                    user.set_unusable_password()
                else:
                    for name, attr in defaults.items():
                        current_attr = getattr(user, name, None)
                        if current_attr != attr:
                            setattr(user, name, attr)
                            updated = True
                    if updated:
                        logger.debug("Updated user %s" % username)

                for path in user_callbacks:
                    callback = import_string(path)
                    callback(user, attributes, created, updated)

                user.save()

                if removed_user_callbacks:
                    ldap_usernames.add(username)

        if removed_user_callbacks:
            django_usernames = set(model.objects.values_list(username_field, flat=True))
            for username in django_usernames - ldap_usernames:
                user = model.objects.get(**{username_field: username})
                for path in removed_user_callbacks:
                    callback = import_string(path)
                    callback(user)
                    logger.debug("Called %s for user %s" % (path, username))

        logger.info("Users are synchronized")

    def get_ldap_groups(self):
        """Retrieve groups from LDAP server."""
        group_filter = get_setting('LDAP_SYNC_GROUP_FILTER')
        if not group_filter:
            logger.debug('LDAP_SYNC_GROUP_FILTER not configured, skipping group sync')
            return None

        group_attributes = get_setting('LDAP_SYNC_GROUP_ATTRIBUTES', strict=True)

        groups = self.ldap_search(group_filter, group_attributes.keys())
        logger.debug("Retrieved %d groups" % len(groups))
        return groups

    def sync_ldap_groups(self, ldap_groups):
        """Synchronize LDAP groups with local group model."""
        group_attributes = get_setting('LDAP_SYNC_GROUP_ATTRIBUTES')
        groupname_field = 'name'

        if groupname_field not in group_attributes.values():
            error_msg = "LDAP_SYNC_GROUP_ATTRIBUTES must contain the field '%s'" % groupname_field
            raise ImproperlyConfigured(error_msg)

        for cname, ldap_attributes in ldap_groups:
            defaults = {}
            try:
                for name, attribute in ldap_attributes.items():
                    defaults[group_attributes[name]] = attribute[0].decode('utf-8')
            except AttributeError:
                # In some cases attrs is a list instead of a dict; skip these invalid groups
                continue

            try:
                groupname = defaults[groupname_field]
            except KeyError:
                logger.warning("Group is missing a required attribute '%s'" % groupname_field)
                continue

            kwargs = {
                groupname_field + '__iexact': groupname,
                'defaults': defaults,
            }

            try:
                group, created = Group.objects.get_or_create(**kwargs)
            except (IntegrityError, DataError) as e:
                logger.error("Error creating group %s: %s" % (groupname, e))
            else:
                if created:
                    logger.debug("Created group %s" % groupname)

        logger.info("Groups are synchronized")

    def ldap_search(self, filter, attributes):
        """
        Query the configured LDAP server with the provided search filter and
        attribute list.
        """
        uri = get_setting('LDAP_SYNC_URI', strict=True)
        base_user = get_setting('LDAP_SYNC_BASE_USER', strict=True)
        base_pass = get_setting('LDAP_SYNC_BASE_PASS', strict=True)
        base = get_setting('LDAP_SYNC_BASE', strict=True)

        ldap.set_option(ldap.OPT_REFERRALS, 0)
        l = PagedLDAPObject(uri)
        l.protocol_version = 3
        try:
            l.simple_bind_s(base_user, base_pass)
        except ldap.LDAPError:
            logger.error("Error connecting to LDAP server %s" % uri)
            raise

        results = l.paged_search_ext_s(base, ldap.SCOPE_SUBTREE, filter, attrlist=attributes, serverctrls=None)
        l.unbind_s()
        return results


class PagedResultsSearchObject:
    """
    Taken from the python-ldap paged_search_ext_s.py demo, showing how to use
    the paged results control: https://bitbucket.org/jaraco/python-ldap/
    """
    page_size = get_setting('LDAP_SYNC_PAGE_SIZE', default=100)

    def paged_search_ext_s(self, base, scope, filterstr='(objectClass=*)', attrlist=None, attrsonly=0,
                           serverctrls=None, clientctrls=None, timeout=-1, sizelimit=0):
        """
        Behaves exactly like LDAPObject.search_ext_s() but internally uses the
        simple paged results control to retrieve search results in chunks.
        """
        req_ctrl = SimplePagedResultsControl(True, size=self.page_size, cookie='')

        # Send first search request
        msgid = self.search_ext(base, ldap.SCOPE_SUBTREE, filterstr, attrlist=attrlist,
                                serverctrls=(serverctrls or []) + [req_ctrl])
        results = []

        while True:
            rtype, rdata, rmsgid, rctrls = self.result3(msgid)
            results.extend(rdata)
            # Extract the simple paged results response control
            pctrls = [c for c in rctrls if c.controlType == SimplePagedResultsControl.controlType]

            if pctrls:
                if pctrls[0].cookie:
                    # Copy cookie from response control to request control
                    req_ctrl.cookie = pctrls[0].cookie
                    msgid = self.search_ext(base, ldap.SCOPE_SUBTREE, filterstr, attrlist=attrlist,
                                            serverctrls=(serverctrls or []) + [req_ctrl])
                else:
                    break

        return results


class PagedLDAPObject(LDAPObject, PagedResultsSearchObject):
    pass
