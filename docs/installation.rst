.. _installation:

Installation
============

Prerequisites
-------------

The primary prerequisite of django-ldap-sync is `Django`_ itself. For
django-ldap-sync |version|, Django 1.4 or later is required. Earlier versions
of Django may work, but are not tested or supported. See the `Django
downloads`_ page for information on downloading and installing Django.

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

First, add django-ldap-sync to the ``INSTALLED_APPS`` setting within your
project's ``settings.py`` (or equivalent) file::

   INSTALLED_APPS = (
       # ...
       'mama_cas',
   )

django-ldap-sync also has a number of required settings that will need to be
configured before it can operate. See the :ref:`settings` documentation for
more information on both required and optional settings.

.. _Django: http://www.djangoproject.com/
.. _Django downloads: https://www.djangoproject.com/download/
.. _requests: http://python-requests.org/
.. _virtualenv: http://www.virtualenv.org/
.. _pip: http://www.pip-installer.org/
.. _PyPI: https://pypi.python.org/pypi/django-ldap-sync/
.. _GitHub: https://github.com/jbittel/django-ldap-sync
.. _tarball: https://github.com/jbittel/django-ldap-sync/tarball/master
