from rest_framework import serializers
from .models import CaseEvent


class CaseEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseEvent
        fields = ["id", "event_type", "from_status", "to_status", "payload", "created_by", "created_at"]
