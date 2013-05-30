django-ldap-sync
================

django-ldap-sync provides a Django management command that synchronizes LDAP
users and groups from an authoritative server. It performs a one-way
synchronization that creates and/or updates the local Django users and groups.

This synchronization is performed each time the management command is run and
can be fired manually on demand, via an automatic cron script or as a periodic
`Celery`_ task.

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

.. _Celery: http://www.celeryproject.org
.. _settings: http://django-ldap-sync.readthedocs.org/en/latest/settings.html
.. _django-ldap-sync.readthedocs.org: http://django-ldap-sync.readthedocs.org
