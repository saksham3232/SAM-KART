from django.core.exceptions import PermissionDenied

class CheckPremiumGroupMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.groups.filter(name='premium').exists():
            return super().dispatch(request, *args, **kwargs)
            # return True
        else:
            raise PermissionDenied
