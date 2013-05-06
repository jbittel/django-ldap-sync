django-ldap-sync
================

django-ldap-sync provides a Django management command for synchronizing LDAP
users and groups. It performs a one-way synchronization to keep the local
Django users in line with an authoritative LDAP server.

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

Initially inspired by `this snippet`_.

.. _this snippet: http://djangosnippets.org/snippets/893/
