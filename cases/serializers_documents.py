from rest_framework import serializers
from .models import CaseDocument, DocumentCategory

class CaseDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseDocument
        fields = [
            "id",
            "case",
            "category",
            "file_url",
            "public_id",
            "original_name",
            "size_bytes",
            "mime_type",
            "uploaded_by",
            "created_at",
        ]
        read_only_fields = ["id", "uploaded_by", "created_at"]


class CaseDocumentUploadSerializer(serializers.Serializer):
    case_id = serializers.IntegerField()
    category = serializers.ChoiceField(choices=DocumentCategory.choices, required=False)
    file = serializers.FileField()

    def validate(self, attrs):
        f = attrs["file"]
        max_mb = 10
        if f.size > max_mb * 1024 * 1024:
            raise serializers.ValidationError(f"Archivo demasiado grande. Máximo {max_mb}MB.")
        return attrs
