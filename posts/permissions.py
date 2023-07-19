from rest_framework.permissions import BasePermission
from rest_framework import permissions


class IsAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.owner



class IsAuthorOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user.is_staff:
            return True
        return request.user == obj.owner


class IsSeller(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_seller


class IsBuyer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_buyer
