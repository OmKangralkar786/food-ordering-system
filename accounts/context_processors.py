from .decorators import is_admin_user


def user_roles(request):
    return {
        'is_admin_user': is_admin_user(request.user),
    }
