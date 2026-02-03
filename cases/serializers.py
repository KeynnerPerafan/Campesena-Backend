from rest_framework import serializers
from .models import Case, CaseStatus


class CaseSerializer(serializers.ModelSerializer):
    can_edit = serializers.SerializerMethodField()

    class Meta:
        model = Case
        fields = [
            "id",
            "code",
            "applicant_type",
            "request_type",
            "status",
            "data",
            "created_by",
            "assigned_to",
            "created_at",
            "updated_at",
            "can_edit",
        ]
        read_only_fields = [
            "id",
            "code",
            "status",
            "created_by",
            "assigned_to",
            "created_at",
            "updated_at",
            "can_edit",
        ]

    def get_can_edit(self, obj):
        return obj.can_edit()


class CaseCreateSerializer(serializers.ModelSerializer):
    uuid_externo = serializers.UUIDField(source="external_uuid", required=False, allow_null=True)
    status = serializers.ChoiceField(choices=[CaseStatus.BORRADOR, CaseStatus.REGISTRADA], required=False)

    class Meta:
        model = Case
        fields = ["id", "applicant_type", "request_type", "data", "status", "uuid_externo"]

    def validate(self, attrs):
        request = self.context["request"]
        user = request.user

        applicant_type = attrs.get("applicant_type")
        request_type = attrs.get("request_type")
        data = attrs.get("data") or {}
        status = attrs.get("status", CaseStatus.BORRADOR)

        # 1) Asegurar que campesino cree como CAMPESINO (no como ASOCIACION)
        if user.role == "CAMPESINO" and applicant_type != "CAMPESINO":
            raise serializers.ValidationError("Un usuario CAMPESINO solo puede crear solicitudes tipo CAMPESINO.")
        if user.role == "ASOCIACION" and applicant_type != "ASOCIACION":
            raise serializers.ValidationError("Un usuario ASOCIACION solo puede crear solicitudes tipo ASOCIACION.")

        # 2) Validaciones mínimas por tipo (ajústalas a lo que ustedes definan)
        required_common = ["municipio", "actividad_productiva", "descripcion_idea"]
        required_cap = required_common + ["tema_capacitacion"]
        required_proj = required_common + ["monto_estimado"]

        if status == CaseStatus.REGISTRADA:
            if request_type == "CAPACITACION":
                missing = [k for k in required_cap if not data.get(k)]
            else:  # PROYECTO_PRODUCTIVO
                missing = [k for k in required_proj if not data.get(k)]

            if missing:
                raise serializers.ValidationError(
                    {"data": f"Faltan campos obligatorios para enviar como REGISTRADA: {', '.join(missing)}"}
                )

        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        status = validated_data.pop("status", CaseStatus.BORRADOR)
        case = Case.objects.create(created_by=request.user, status=status, **validated_data)
        return case


class CaseUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case
        fields = ["data"]

    def validate(self, attrs):
        case: Case = self.instance
        if not case.can_edit():
            raise serializers.ValidationError("Esta solicitud no se puede editar en el estado actual.")
        return attrs

class CaseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case
        fields = ["id", "applicant_type", "request_type", "status", "created_at", "updated_at"]