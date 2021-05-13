from rest_framework.permissions import BasePermission

SAFE_METHODS = ["GET", "POST"]
PROTECTED_METHODS = ["PUT", "PATCH", "DELETE"]


class ProjectPostPermissions(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS and (request.user in obj.users or request.user == obj.owner):
            return True
        elif request.method in PROTECTED_METHODS and obj.owner == request.user:
            return True
        return False
