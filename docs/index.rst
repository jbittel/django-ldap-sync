.. django-ldap-sync documentation master file, created by
   sphinx-quickstart on Sun May  5 21:33:04 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

django-ldap-sync documentation
==============================

django-ldap-sync provides a Django management command that synchronizes LDAP
users and groups from an authoritative server. It performs a one-way
synchronization that creates and/or updates the local Django users and groups.

This synchronization is performed each time the management command is run and
can be fired manually on demand, via an automatic cron script or as a periodic
`Celery`_ task.

Contents
--------

.. toctree::
   :maxdepth: 2

   installation
   settings
   changelog

Credits
-------

Initially inspired by `this snippet`_.

.. _Celery: http://www.celeryproject.org
.. _this snippet: http://djangosnippets.org/snippets/893/
