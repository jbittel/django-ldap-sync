from celery import shared_task

from ldap_sync.sync import SyncLDAP


@shared_task
def syncldap():
    sync_ldap = SyncLDAP()
    sync_ldap.sync_groups()
    sync_ldap.sync_users()
