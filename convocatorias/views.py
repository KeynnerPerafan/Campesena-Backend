from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsAdmin
from .models import Convocatoria
from .serializers import ConvocatoriaSerializer

class AdminConvocatoriaViewSet(viewsets.ModelViewSet):
    queryset = Convocatoria.objects.all().order_by("-id")
    serializer_class = ConvocatoriaSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
