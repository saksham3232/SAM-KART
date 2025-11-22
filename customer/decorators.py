from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test

def group_required(group, login_url=None, raise_exception=False):
    def check_perms(user):
        if isinstance(group, str):
            groups = (group,)
        else:
            groups = group

        if user.is_authenticated and user.groups.filter(name__in=groups).exists():
            return True

        if raise_exception:
            raise PermissionDenied

        return False

    return user_passes_test(check_perms, login_url=login_url)
