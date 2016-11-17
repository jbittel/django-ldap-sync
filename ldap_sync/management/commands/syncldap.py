import logging

from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import DataError
from django.db import IntegrityError
from django.utils.module_loading import import_string

from ldap_sync.search import LDAPSearch
from ldap_sync.utils import get_setting


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    can_import_settings = True
    help = 'Synchronize users and groups from an authoritative LDAP server'

    def handle(self, *args, **options):
        ldap = LDAPSearch()

        group_filter = get_setting('LDAP_SYNC_GROUP_FILTER')
        if group_filter:
            group_attributes = get_setting('LDAP_SYNC_GROUP_ATTRIBUTES', strict=True)
            ldap_groups = ldap.search(group_filter, group_attributes.keys())
            self.sync_ldap_groups(ldap_groups)

        user_filter = get_setting('LDAP_SYNC_USER_FILTER')
        if user_filter:
            user_attributes = get_setting('LDAP_SYNC_USER_ATTRIBUTES', strict=True)
            user_attributes_keys = set(user_attributes.keys())
            user_extra_attributes = get_setting('LDAP_SYNC_USER_EXTRA_ATTRIBUTES', default=[])
            user_attributes_keys.update(user_extra_attributes)
            ldap_users = ldap.search(user_filter, user_attributes_keys)
            self.sync_ldap_users(ldap_users)

        ldap.unbind()

    def sync_ldap_groups(self, ldap_groups):
        """Synchronize LDAP groups with local group model."""
        group_attributes = get_setting('LDAP_SYNC_GROUP_ATTRIBUTES', strict=True)
        groupname_field = 'name'

        if groupname_field not in group_attributes.values():
            raise ImproperlyConfigured("LDAP_SYNC_GROUP_ATTRIBUTES must contain the field '%s'" % groupname_field)

        for cname, ldap_attributes in ldap_groups:
            defaults = {}

            if not isinstance(ldap_attributes, dict):
                # In some cases attrs is not a dict; skip these invalid groups
                continue

            for ldap_name, field in group_attributes.items():
                try:
                    defaults[field] = group_attributes[ldap_name][0].decode('utf-8')
                except KeyError:
                    defaults[field] = ''

            groupname = defaults[groupname_field]
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

    def sync_ldap_users(self, ldap_users):
        """Synchronize users with local user model."""
        model = get_user_model()
        user_attributes = get_setting('LDAP_SYNC_USER_ATTRIBUTES', strict=True)
        username_field = get_setting('LDAP_SYNC_USERNAME_FIELD')
        if username_field is None:
            username_field = getattr(model, 'USERNAME_FIELD', 'username')
        user_callbacks = list(get_setting('LDAP_SYNC_USER_CALLBACKS', default=[]))
        removed_user_callbacks = list(get_setting('LDAP_SYNC_REMOVED_USER_CALLBACKS', default=[]))
        ldap_usernames = set()

        if not model._meta.get_field(username_field).unique:
            raise ImproperlyConfigured("Field '%s' must be unique" % username_field)

        if username_field not in user_attributes.values():
            raise ImproperlyConfigured("LDAP_SYNC_USER_ATTRIBUTES must contain the field '%s'" % username_field)

        for cname, ldap_attributes in ldap_users:
            defaults = {}

            if not isinstance(ldap_attributes, dict):
                # In some cases attributes is not a dict; skip these invalid users
                continue

            for ldap_name, field in user_attributes.items():
                try:
                    defaults[field] = ldap_attributes[ldap_name][0].decode('utf-8')
                except KeyError:
                    defaults[field] = ''

            username = defaults[username_field].lower()
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
                    callback(user, ldap_attributes, created, updated)

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
