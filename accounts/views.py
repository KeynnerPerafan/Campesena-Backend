from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response

from .serializers import UserCreateSerializer, MeSerializer
from .permissions import IsAdmin

User = get_user_model()


class AdminUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("-id")
    serializer_class = UserCreateSerializer
    permission_classes = [IsAdmin]

    @action(detail=True, methods=["put"], url_path="activar")
    def activar(self, request, pk=None):
        user = self.get_object()
        user.is_active = True
        user.save(update_fields=["is_active"])
        return Response({"id": user.id, "is_active": user.is_active}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["put"], url_path="desactivar")
    def desactivar(self, request, pk=None):
        user = self.get_object()
        user.is_active = False
        user.save(update_fields=["is_active"])
        return Response({"id": user.id, "is_active": user.is_active}, status=status.HTTP_200_OK)


@api_view(["GET"])
def me(request):
    return Response(MeSerializer(request.user).data)
