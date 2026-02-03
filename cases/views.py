from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Case
from .serializers import (
    CaseSerializer,
    CaseCreateSerializer,
    CaseUpdateSerializer,
    CaseListSerializer,
)
from .permissions import CanAccessCase

from audit.models import CaseEvent, EventType
from audit.serializers import CaseEventSerializer


class CaseViewSet(viewsets.ModelViewSet):
    queryset = Case.objects.select_related("created_by", "assigned_to").all().order_by("-id")
    permission_classes = [IsAuthenticated, CanAccessCase]

    def get_queryset(self):
        user = self.request.user

        # ✅ query param: /solicitudes?mias=true
        mias = (self.request.query_params.get("mias") or "").lower() in ["true", "1", "yes"]

        if mias:
            return self.queryset.filter(created_by=user)

        # comportamiento normal:
        # - ADMIN/GESTOR: ven todo
        # - CAMPESINO/ASOCIACION: ven solo lo suyo
        if user.role in ["ADMIN", "GESTOR"]:
            return self.queryset
        return self.queryset.filter(created_by=user)

    def get_serializer_class(self):
        # ✅ listado ligero para la app (estado, tipo, fechas)
        if self.action == "list":
            return CaseListSerializer

        if self.action == "create":
            return CaseCreateSerializer

        if self.action in ["update", "partial_update"]:
            return CaseUpdateSerializer

        return CaseSerializer

    def perform_create(self, serializer):
        case = serializer.save()
        CaseEvent.objects.create(
            case=case,
            event_type=EventType.CREATED,
            to_status=case.status,
            payload={"applicant_type": case.applicant_type, "request_type": case.request_type},
            created_by=self.request.user,
        )

    def perform_update(self, serializer):
        case_before = self.get_object()
        case = serializer.save()

        status_changed = case_before.status != case.status

        CaseEvent.objects.create(
            case=case,
            event_type=EventType.STATUS_CHANGED if status_changed else EventType.UPDATED,
            from_status=case_before.status if status_changed else "",
            to_status=case.status if status_changed else "",
            payload={"action": "status_change"} if status_changed else {"changed": "data"},
            created_by=self.request.user,
        )


    @action(detail=True, methods=["GET"])
    def timeline(self, request, pk=None):
        case = self.get_object()
        events = CaseEvent.objects.filter(case=case).order_by("created_at")
        return Response(CaseEventSerializer(events, many=True).data)
