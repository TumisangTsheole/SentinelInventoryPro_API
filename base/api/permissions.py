from rest_framework import permissions

class IsViewer(permissions.BasePermission):
    """Allow access only to users in Viewer group or above."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.groups.filter(name='Viewer').exists() or
            request.user.groups.filter(name='Stocker').exists() or
            request.user.groups.filter(name='Admin').exists() or
            request.user.is_superuser
        )

class IsStocker(permissions.BasePermission):
    #Allow access only to users in Stocker group or above.
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.groups.filter(name='Stocker').exists() or
            request.user.groups.filter(name='Admin').exists() or
            request.user.is_superuser
        )

class IsAdmin(permissions.BasePermission):
    #Allow access only to users in Admin group or superuser.
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.groups.filter(name='Admin').exists() or
            request.user.is_superuser
        )
