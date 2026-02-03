from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class LoginSerializer(serializers.Serializer):
    document_type = serializers.CharField(required=False, allow_blank=True)
    document_number = serializers.CharField(required=False, allow_blank=True)
    document_id = serializers.CharField(required=False, allow_blank=True)  # fallback
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        doc_type = (attrs.get("document_type") or "").strip()
        doc_number = (attrs.get("document_number") or "").strip()
        doc_id = (attrs.get("document_id") or "").strip()
        password = attrs.get("password")

        user = None

        # Preferido: type + number
        if doc_type and doc_number:
            user = User.objects.filter(document_type=doc_type, document_number=doc_number).first()

        # Fallback: document_id
        if user is None and doc_id:
            user = User.objects.filter(document_id=doc_id).first()

        if user is None:
            raise serializers.ValidationError({"detail": "Credenciales inválidas."})

        if not user.check_password(password):
            raise serializers.ValidationError({"detail": "Credenciales inválidas."})

        if not user.is_active:
            raise serializers.ValidationError({"detail": "Usuario inactivo."})

        attrs["user"] = user
        return attrs
