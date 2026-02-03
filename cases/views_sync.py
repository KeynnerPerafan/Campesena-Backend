from django.db import transaction
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Case, CaseStatus
from .serializers_sync import SyncSolicitudesSerializer
from audit.models import CaseEvent, EventType


class SyncSolicitudesView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        ser = SyncSolicitudesSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        submit_all = ser.validated_data.get("submit", False)
        items = ser.validated_data["solicitudes"]

        mapping = {}
        created = 0
        updated = 0

        for item in items:
            ext_uuid = item["uuid_externo"]
            applicant_type = item["applicant_type"]
            request_type = item["request_type"]
            data = item.get("data", {}) or {}
            desired_status = item.get("status", CaseStatus.BORRADOR)
            if submit_all:
                desired_status = CaseStatus.REGISTRADA

            # ✅ idempotente: si existe ese external_uuid, NO se crea otro
            case = Case.objects.filter(external_uuid=ext_uuid).first()

            if case:
                # seguridad: si el uuid existe pero no es del usuario, no lo tocamos
                if case.created_by_id != request.user.id:
                    continue

                # opcional: actualizar data si venía más reciente
                # (MVP: merge simple)
                case.data = data or case.data

                # si se pide REGISTRADA y está en BORRADOR, lo subimos
                if desired_status == CaseStatus.REGISTRADA and case.status == CaseStatus.BORRADOR:
                    case.status = CaseStatus.REGISTRADA
                case.save(update_fields=["data", "status", "updated_at"])

                mapping[str(ext_uuid)] = case.id
                updated += 1
                continue

            # crear nueva
            case = Case.objects.create(
                applicant_type=applicant_type,
                request_type=request_type,
                data=data,
                status=desired_status,
                created_by=request.user,
                external_uuid=ext_uuid,
            )

            CaseEvent.objects.create(
                case=case,
                event_type=EventType.CREATED,
                to_status=case.status,
                payload={"source": "offline_sync"},
                created_by=request.user,
            )

            mapping[str(ext_uuid)] = case.id
            created += 1

        return Response(
            {"mapping": mapping, "created": created, "updated": updated},
            status=status.HTTP_200_OK,
        )
