django-ldap-sync
================

django-ldap-sync provides a Django management command for synchronizing LDAP
users and groups. It performs a one-way synchronization to create and update
local Django users and groups.

Quickstart
----------

#. Install the application::

      pip install django-ldap-sync

#. Append it to the installed apps::

      INSTALLED_APPS = (
          # ...
          'ldap_sync',
      )

#. Configure the required `settings`_.

#. Run the synchronization management command::

      manage.py syncldap

For more information on installation and configuration, see the included
documentation or read the documentation online at
`django-ldap-sync.readthedocs.org`_.

.. _settings: http://django-ldap-sync.readthedocs.org/en/latest/settings.html
.. _django-ldap-sync.readthedocs.org: http://django-ldap-sync.readthedocs.org
