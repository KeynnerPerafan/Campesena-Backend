from rest_framework import serializers
from .models import Convocatoria, ConvocatoriaStatus

class ConvocatoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Convocatoria
        fields = [
            "id",
            "title",
            "description",
            "start_date",
            "end_date",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        start = attrs.get("start_date", getattr(self.instance, "start_date", None))
        end = attrs.get("end_date", getattr(self.instance, "end_date", None))

        if start and end and start > end:
            raise serializers.ValidationError("start_date no puede ser mayor que end_date")

        # status sólo ABIERTA/CERRADA (ya lo hace choices)
        return attrs
