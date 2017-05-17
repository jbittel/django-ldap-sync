.. _installation:

Installation
============

Prerequisites
-------------

django-ldap-sync |version| has two required prerequisites:

   * `Django`_ 1.8 or later
   * `python-ldap`_ 2.4.13 or later

The automatic installation options below will install or update python-ldap as
necessary. Earlier versions of these dependencies may work, but are not tested
or supported.

Installing
----------

There are several different ways to install django-ldap-sync, depending on
your preferences and needs. In all cases, it is recommended to run the
installation within a `virtualenv`_ for isolation from other Python system
packages.

Via pip
~~~~~~~

The easiest installation method is with `pip`_::

   pip install django-ldap-sync

Via a downloaded package
~~~~~~~~~~~~~~~~~~~~~~~~

If you cannot access pip or prefer to install the package manually, download
the tarball from `PyPI`_. Extract the downloaded archive and install it with::

   python setup.py install

Via GitHub
~~~~~~~~~~

To stay current with the latest development, clone the active development
repository on `GitHub`_::

   git clone git://github.com/jbittel/django-ldap-sync.git

If you don't want a full git repository, download the latest code from GitHub
as a `tarball`_.

Configuring
-----------

Add django-ldap-sync to the ``INSTALLED_APPS`` setting within your project's
``settings.py`` (or equivalent) file::

   INSTALLED_APPS = (
       # ...
       'ldap_sync',
   )

django-ldap-sync has a number of required settings that must be configured
before it can operate. See the :ref:`settings` documentation for a complete
list of the required and optional settings.

Running
-------

There are several tools available to synchronize data depending on your needs
and environment.

Management Command
~~~~~~~~~~~~~~~~~~

A management command is included to run manual synchronizations. It can also
be run as part of an automated cron task. Run the command with::

   python manage.py syncldap

Celery
~~~~~~

A Celery task is included to make the synchronization task more distributed.
Assuming Celery is installed and configured, only some additional
configuration is required within your project's ``settings.py`` file::

   from datetime import timedelta

   CELERY_BEAT_SCHEDULE = {
       'synchronize_ldap': {
           'task': 'ldap_sync.tasks.syncldap',
           'schedule': timedelta(minutes=30),
       },
   }

Code
~~~~

For complete control or to integrate it with other functionality, the
synchronization can also be performed directly in code::

   from ldap_sync.sync import SyncLDAP

   sync_ldap = SyncLDAP()
   sync_ldap.sync_groups()
   sync_ldap.sync_users()

For more information and other configuration options, see the Celery
documentation on `periodic tasks`_.

.. _Django: http://www.djangoproject.com/
.. _python-ldap: http://www.python-ldap.org/
.. _Django downloads: https://www.djangoproject.com/download/
.. _virtualenv: http://www.virtualenv.org/
.. _pip: http://www.pip-installer.org/
.. _PyPI: https://pypi.python.org/pypi/django-ldap-sync/
.. _GitHub: https://github.com/jbittel/django-ldap-sync
.. _tarball: https://github.com/jbittel/django-ldap-sync/tarball/master
.. _Celery: http://www.celeryproject.org
.. _periodic tasks: http://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html
