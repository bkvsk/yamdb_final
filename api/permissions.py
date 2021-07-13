from django.contrib.auth import get_user_model
from rest_framework.permissions import SAFE_METHODS, BasePermission

User = get_user_model()


class IsPostOrIsAuthorOrNotUserOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in ('POST', *SAFE_METHODS)
            or hasattr(request.user, 'is_not_user')
            and request.user.is_not_user()
            or obj.author == request.user
        )


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or hasattr(request.user, 'is_admin')
                and request.user.is_admin())


class UserRolePermission(BasePermission):
    role = []

    def has_permission(self, request, view):
        if not request.user:
            return False
        return bool(
            hasattr(request.user, 'is_admin') and request.user.is_admin()
            or hasattr(request.user, 'role') and request.user.role in self.role
        )


class IsUserOrAdmin(UserRolePermission):
    role = [User.Role.USER]


class IsModeratorOrAdmin(UserRolePermission):
    role = [User.Role.MODERATOR]


class IsAdmin(UserRolePermission):
    pass


class IsAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or obj.author == request.user)
