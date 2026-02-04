from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import AdminUserViewSet
from .views_auth import LoginView
from .views_me import MeView

router = DefaultRouter()
router.register(r"admin/users", AdminUserViewSet, basename="admin-users")

urlpatterns = [
    # Admin
    path("", include(router.urls)),

    # Auth
    path("auth/login/", LoginView.as_view(), name="auth-login"),

    # Usuario autenticado
    path("me/", MeView.as_view(), name="me"),
]
