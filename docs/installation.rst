.. _installation:

Installation
============

Prerequisites
-------------

django-ldap-sync |version| has two required prerequisites:

   * `Django`_ 1.5 or later
   * `python-ldap`_ 2.4.10 or later

Earlier versions of these dependencies may work, but are not tested or
supported.

Installing
----------

There are several different ways to install django-ldap-sync, depending on
your preferences and needs. In all cases, it is recommended to run the
installation within a `virtualenv`_ for isolation from other system packages.

Via pip
~~~~~~~

The easiest way to install it is with `pip`_::

   pip install django-ldap-sync

Via a downloaded package
~~~~~~~~~~~~~~~~~~~~~~~~

If you cannot access pip or prefer to install the package manually, download
it from `PyPI`_. Extract the downloaded archive and install it with::

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
before it can operate. See the :ref:`settings` documentation for more
information on the required and optional settings.

Celery
~~~~~~

Typically you will want to run this management command on a regular basis to
keep the users synchronized. One way to accomplish this is using a
periodic Celery task. This requires additional configuration within your
settings file::

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
.. _periodic tasks: http://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html
