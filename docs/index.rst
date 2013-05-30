.. django-ldap-sync documentation master file, created by
   sphinx-quickstart on Sun May  5 21:33:04 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

django-ldap-sync documentation
==============================

django-ldap-sync provides a Django management command for synchronizing LDAP
users and groups. It performs one-way synchronization to add and update the
local Django users and groups.

This management command can be fired manually on demand, via an automatic
cron script or as a periodic `Celery`_ task.

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
