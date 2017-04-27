from django.core.management.base import BaseCommand

from ldap_sync.sync import SyncLDAP


class Command(BaseCommand):
    can_import_settings = True
    help = 'Synchronize users and groups from an authoritative LDAP server'

    def handle(self, *args, **options):
        sync_ldap = SyncLDAP()
        sync_ldap.sync_groups()
        sync_ldap.sync_users()
