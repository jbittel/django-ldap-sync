def user_active_directory_enabled(user, attributes, created, updated):
    """
    Activate/deactivate user accounts based on Active Directory's
    userAccountControl flags. Requires 'userAccountControl'
    to be included in LDAP_SYNC_USER_EXTRA_ATTRIBUTES.
    """
    try:
        user_account_control = int(attributes['userAccountControl'][0])
        if user_account_control & 2:
            user.is_active = False
        else:
            user.is_active = True
    except KeyError:
        pass


def removed_user_deactivate(user):
    """
    Deactivate user accounts that no longer appear in the
    source LDAP server.
    """
    if user.is_active:
        user.is_active = False
        user.save()


def removed_user_delete(user):
    """
    Delete user accounts that no longer appear in the
    source LDAP server.
    """
    user.delete()
