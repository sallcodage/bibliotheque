from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """
    Lecture libre pour tous.
    Écriture (POST, PUT, DELETE) réservée aux administrateurs.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:  # GET, HEAD, OPTIONS
            return True
        return request.user and request.user.is_staff


class IsOwnerOrAdmin(BasePermission):
    """
    L'emprunteur peut voir/modifier son propre emprunt.
    Les admins ont accès à tout.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.emprunteur == request.user
