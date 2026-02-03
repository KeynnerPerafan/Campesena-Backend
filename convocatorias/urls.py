from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdminConvocatoriaViewSet

router = DefaultRouter()
router.register(r"admin/convocatorias", AdminConvocatoriaViewSet, basename="admin-convocatorias")

urlpatterns = [
    path("", include(router.urls)),
]
