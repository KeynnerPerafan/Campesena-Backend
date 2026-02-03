from rest_framework import serializers
from .models import ApplicantType, RequestType, CaseStatus

class SyncSolicitudItemSerializer(serializers.Serializer):
    uuid_externo = serializers.UUIDField()
    applicant_type = serializers.ChoiceField(choices=ApplicantType.choices)
    request_type = serializers.ChoiceField(choices=RequestType.choices)
    data = serializers.JSONField(required=False)
    # opcional: si offline ya decidió enviarla
    status = serializers.ChoiceField(choices=[CaseStatus.BORRADOR, CaseStatus.REGISTRADA], required=False)

class SyncSolicitudesSerializer(serializers.Serializer):
    solicitudes = SyncSolicitudItemSerializer(many=True)
    # si true, fuerza todas a REGISTRADA (útil botón "Sincronizar y enviar")
    submit = serializers.BooleanField(required=False, default=False)
