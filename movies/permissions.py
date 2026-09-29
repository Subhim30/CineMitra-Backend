from rest_framework.permissions import BasePermission


class IsVendor(BasePermission):
    """
    Allows access only to authenticated users
    whose UserProfile role is VENDOR.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        try:
            return request.user.userprofile.role == "VENDOR"
        except Exception:
            return False