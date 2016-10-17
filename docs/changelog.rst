.. _changelog:

Changelog
=========

These are the notable changes for each django-ldap-sync release. For
additional detail, read the complete `commit history`_.

**django-ldap-sync 0.4.1**
   * Additionally enable users in AD callback

**django-ldap-sync 0.4.0**
   * Fix error when synchronizing groups
   * Add setting to retrieve additional LDAP attributes
   * Pass attributes to user callback functions
   * Add example callback for disabling users with AD userAccountControl

**django-ldap-sync 0.3.2**
   * Fix packaging errors

**django-ldap-sync 0.3.0**
   * Add a setting to override the username field
   * Add handling of removed users
   * Implement callbacks for added/changed and removed users

**django-ldap-sync 0.2.0**
   * Handle DataError exception when syncing long names (thanks @tomrenn!)
   * Change Celery task to use @shared_task decorator

**django-ldap-sync 0.1.1**
   * Fix exception with AD internal referrals

**django-ldap-sync 0.1.0**
   * Initial release

.. _commit history: https://github.com/jbittel/django-ldap-sync/commits/
