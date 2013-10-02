.. _installation:

Installation
============

Prerequisites
-------------

django-ldap-sync |version| has two required prerequisites:

   * `Django`_ 1.5 or later
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

django-ldap-sync has a number of required settings that need to be configured
before it can operate. See the :ref:`settings` documentation for a complete
list of the required and optional settings.

Running
-------

Typically you will want to run this management command on a regular basis to
keep the users synchronized. There are several ways to accomplish this
depending on your needs and environment.

Manual
~~~~~~

The management command can always be run manually, which might be sufficient
for some simple or relatively static environments. Run the command with::

   python manage.py ldap_sync

Cron
~~~~

The next logical step from running the command manually is to automate running
it on a regular basis with cron (or your system's equivalent). The
implementation details depend on your system and environment. If you do not
have access to the local system cron, consider `django-cron`_ or
`django-poormanscron`_.

Celery
~~~~~~

Another methodology is to run the command as a periodic `Celery`_ task.
Particularly if you already have Celery available, this can be a good way to
run the command in a more distributed fashion. django-ldap-sync comes with a
Celery task that wraps the management command, so only some additional
configuration is required within your project's ``settings.py`` file::

   from datetime import timedelta

   CELERYBEAT_SCHEDULE = {
       'synchronize_local_users': {
           'task': 'ldap_sync.tasks.syncldap',
           'schedule': timedelta(minutes=30),
       }
   }

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
.. _django-cron: http://code.google.com/p/django-cron/
.. _django-poormanscron: http://code.google.com/p/django-poormanscron/
.. _Celery: http://www.celeryproject.org
.. _periodic tasks: http://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html
