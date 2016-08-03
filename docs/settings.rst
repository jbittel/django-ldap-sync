.. _settings:

Settings
========

.. currentmodule:: django.conf.settings

.. attribute:: LDAP_SYNC_URI

   :default: ``""``

   The address of the LDAP server containing the authoritative user account
   information. This should be a string specifying the complete address::

      LDAP_SYNC_URI = "ldap://users.example.com:389"

.. attribute:: LDAP_SYNC_BASE

   :default: ``""``

   The root of the LDAP tree to search for user account information. The
   contents of this tree can be further refined using the filtering settings.
   This should be a string specifying the complete root path::

      LDAP_SYNC_BASE = "OU=Users,DC=example,DC=com"

.. attribute:: LDAP_SYNC_BASE_USER

   :default: ``""``

   A user with appropriate permissions to connect to the LDAP server and
   retrieve user account information. This should be a string specifying the
   LDAP user account::

      LDAP_SYNC_BASE_USER = "CN=Django,OU=Users,DC=example,DC=com"

.. attribute:: LDAP_SYNC_BASE_PASS

   :default: ``""``

   The corresponding password for the above user account. This should be a
   string specifying the password::

      LDAP_SYNC_BASE_PASS = "My super secret password"

.. attribute:: LDAP_SYNC_USER_FILTER

   :default: ``""``

   An LDAP filter to further refine the user accounts to synchronize. This
   should be a string specifying a valid LDAP filter::

      LDAP_SYNC_USER_FILTER = "(&(objectCategory=person)(objectClass=User)(memberOf=CN=Web,OU=Users,DC=example,DC=com))"

   .. note::

      If this setting is not specified, the user synchronization step will
      be skipped.

.. attribute:: LDAP_SYNC_USER_ATTRIBUTES

   :default: ``{}``

   A dictionary mapping LDAP field names to User profile attributes. New users
   will be created with this data populated, and existing users will be
   updated as necessary. The mapping must at least contain a field mapping
   the User model's username field::

      LDAP_SYNC_USER_ATTRIBUTES = {
          "sAMAccountName": "username",
          "givenName": "first_name",
          "sn": "last_name",
          "mail": "email",
      }

.. attribute:: LDAP_SYNC_USER_CALLBACKS

   :default: ``[]``

   A list of dotted paths to callback functions that will be called for each user
   added or updated. Each callback function is passed three parameters: the user
   object, a created flag and an updated flag.

.. attribute:: LDAP_SYNC_USER_EXTRA_ATTRIBUTES

   :default: ``[]``

   A list of additional LDAP field names to retrieve. These attributes are not
   updated on user accounts, but are passed to user callback functions for
   additional processing.

.. attribute:: LDAP_SYNC_REMOVED_USER_CALLBACKS

   :default: ``[]``

   A list of dotted paths to callback functions that will be called for each user
   found to be removed. Each callback function is passed a single parameter of the
   user object. Note that if changes are made to the user object, it will need to
   be explicitly saved within the callback function.

   Two callback functions are included, providing common functionality:
   ``ldap_sync.callbacks.removed_user_deactivate`` and ``ldap_sync.callbacks.removed_user_delete``
   which deactivate and delete the given user, respectively.

.. attribute:: LDAP_SYNC_USERNAME_FIELD

   :default: ``None``

   An optional field on the synchronized User model to use as the unique key for
   each user. If not specified, the User model's ``USERNAME_FIELD`` will be used.
   If specified, the field must be included in ``LDAP_SYNC_USER_ATTRIBUTES``.

.. attribute:: LDAP_SYNC_GROUP_FILTER

   :default: ``""``

   An LDAP filter string to further refine the groups to synchronize.  This
   should be a string specifying any valid filter string::

      LDAP_SYNC_GROUP_FILTER = "(&(objectclass=group))"

   .. note::

      If this setting is not specified, the group synchronization step will
      be skipped.

.. attribute:: LDAP_SYNC_GROUP_ATTRIBUTES

   :default: ``{}``

   A dictionary mapping LDAP field names to Group attributes. New groups
   will be created with this data populated, and existing groups will be
   updated as necessary. The mapping must at least contain a field with the
   value of ``name`` to specify the group's name::

      LDAP_SYNC_GROUP_ATTRIBUTES = {
          "cn": "name",
      }
