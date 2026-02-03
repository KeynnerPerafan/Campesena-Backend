from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CaseViewSet
from .views_documents import DocumentUploadView, DocumentListView
from .views_sync import SyncSolicitudesView


router = DefaultRouter()
router.register(r"cases", CaseViewSet, basename="cases")

# Aliases para endpoints "bonitos" de la app
solicitudes_list = CaseViewSet.as_view({"get": "list", "post": "create"})
solicitudes_detail = CaseViewSet.as_view({"get": "retrieve", "patch": "partial_update", "put": "update"})

# eventos/timeline con la ruta
solicitudes_eventos = CaseViewSet.as_view({"get": "timeline"})


urlpatterns = [
    path("", include(router.urls)),

    # Solicitudes (alias)
    path("solicitudes/", solicitudes_list, name="solicitudes-list"),
    path("solicitudes/<int:pk>/", solicitudes_detail, name="solicitudes-detail"),

    # Auditoría / Timeline (alias solicitado en Trello)
    path("solicitudes/<int:pk>/eventos/", solicitudes_eventos, name="solicitudes-eventos"),

    # Documentos
    path("documentos/subir/", DocumentUploadView.as_view(), name="documentos-subir"),
    path("documentos/", DocumentListView.as_view(), name="documentos-list"),

    # Sync offline
    path("sync/solicitudes/", SyncSolicitudesView.as_view(), name="sync-solicitudes"),
]
