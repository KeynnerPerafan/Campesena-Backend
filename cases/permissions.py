from rest_framework.permissions import BasePermission, SAFE_METHODS

class CanAccessCase(BasePermission):
    """
    - ADMIN/GESTOR: pueden leer y gestionar (incluye cambiar estado)
    - CAMPESINO/ASOCIACION: pueden crear y editar lo propio (según estado)
    """
    def has_permission(self, request, view):
        # lectura permitida a todos los autenticados
        if request.method in SAFE_METHODS:
            return True

        # crear: solo solicitantes
        if view.action == "create":
            return request.user.role in ["CAMPESINO", "ASOCIACION"]

        # update/partial_update:
        # - ADMIN/GESTOR pueden gestionar
        # - solicitantes pueden editar lo suyo (según estado, lo valida serializer)
        if view.action in ["update", "partial_update"]:
            return request.user.role in ["ADMIN", "GESTOR", "CAMPESINO", "ASOCIACION"]

        # por defecto
        return request.user.role in ["ADMIN", "GESTOR"]

    def has_object_permission(self, request, view, obj):
        if request.user.role in ["ADMIN", "GESTOR"]:
            return True
        return obj.created_by_id == request.user.id
