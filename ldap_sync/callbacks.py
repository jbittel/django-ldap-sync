def removed_user_deactivate(user):
    if user.is_active:
        user.is_active = False
        user.save()


def removed_user_delete(user):
    user.delete()
