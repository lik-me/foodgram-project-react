from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrReadOnly(BasePermission):
    """
    Ограничение прав доступа изменения контента только для админа,
    чтение — для любого пользователя.
    """

    def has_permission(self, request, view):
        # Делаем доступ для анонима к эндпоинту /users/
        # if view.action == 'list' and not 'pk' in request.data:
        if 'pk' in view.kwargs:
            return bool(
                request.user.is_authenticated
            )
        elif 'pk' not in view.kwargs:
            return True
        else:
            return bool(
                request.method in SAFE_METHODS
                or request.user.is_authenticated
                and request.user.is_admin
            )


class IsUserOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return (
                request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
            )

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated and
                obj.author == request.user)


class IsAdmin(BasePermission):
    """
    Ограничение прав доступа изменения контента только для админа.
    """

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_staff or request.user.is_admin
        )


class IsAuthor(BasePermission):
    """
    Ограничение прав доступа изменения контента только для автора.
    """

    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in SAFE_METHODS
            or obj.author == request.user
        )
