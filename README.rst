django-ldap-sync
================

django-ldap-sync provides a Django management command for synchronizing LDAP
users and groups. It performs a one-way synchronization to both add and update
the local Django users and groups.

Quickstart
----------

#. Install the application::

      pip install django-ldap-sync

#. Add it to the installed apps::

      INSTALLED_APPS = (
          # ...
          'ldap_sync',
      )

#. Configure the required settings.

#. Run the synchronization management command::

      manage.py syncldap

For more information on installation or configuration, see the included
documentation.
