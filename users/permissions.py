from rest_framework.permissions import BasePermission

class IsModer(BasePermission):
    """
    Разрешение для модераторов.
    Проверяет, состоит ли пользователь в группе 'moderators'.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.groups.filter(name='moderators').exists()


class IsOwner(BasePermission):
    """
    Разрешение для владельца объекта.
    Пользователь может работать только с объектами, где он owner.
    """
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
