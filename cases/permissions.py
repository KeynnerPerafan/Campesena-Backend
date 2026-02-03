from rest_framework.permissions import BasePermission, SAFE_METHODS

class CanAccessCase(BasePermission):
    """
    - ADMIN/GESTOR: pueden leer (list/detail/timeline)
    - CAMPESINO/ASOCIACION: pueden crear y ver/editar lo propio (según estado)
    """
    def has_permission(self, request, view):
        # lectura permitida a todos los autenticados
        if request.method in SAFE_METHODS:
            return True

        # create/update: solo solicitantes
        if view.action in ["create", "update", "partial_update"]:
            return request.user.role in ["CAMPESINO", "ASOCIACION"]

        # por defecto
        return request.user.role in ["ADMIN", "GESTOR"]

    def has_object_permission(self, request, view, obj):
        if request.user.role in ["ADMIN", "GESTOR"]:
            return True
        return obj.created_by_id == request.user.id
