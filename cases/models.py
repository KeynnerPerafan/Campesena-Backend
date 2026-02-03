from django.conf import settings
from django.db import models
import uuid


class ApplicantType(models.TextChoices):
    CAMPESINO = "CAMPESINO", "Campesino"
    ASOCIACION = "ASOCIACION", "Asociación"


class RequestType(models.TextChoices):
    CAPACITACION = "CAPACITACION", "Capacitación"
    PROYECTO_PRODUCTIVO = "PROYECTO_PRODUCTIVO", "Proyecto productivo"


class CaseStatus(models.TextChoices):
    BORRADOR = "BORRADOR", "Borrador"
    REGISTRADA = "REGISTRADA", "Registrada"
    EN_REVISION = "EN_REVISION", "En revisión"
    EN_AJUSTES = "EN_AJUSTES", "En ajustes"
    VALIDADA = "VALIDADA", "Validada"
    VALIDADA_PARA_ENVIO = "VALIDADA_PARA_ENVIO", "Validada para envío"


class Case(models.Model):
    code = models.CharField(max_length=30, blank=True, default="")
    applicant_type = models.CharField(max_length=20, choices=ApplicantType.choices)
    request_type = models.CharField(max_length=30, choices=RequestType.choices)

    status = models.CharField(max_length=30, choices=CaseStatus.choices, default=CaseStatus.BORRADOR)
    data = models.JSONField(default=dict, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="cases_created")
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="cases_assigned",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # uuid_externo (para que la app mande un id local y no duplique)
    external_uuid = models.UUIDField(null=True, blank=True, unique=True, db_index=True)

    def can_edit(self) -> bool:
        return self.status in [CaseStatus.BORRADOR, CaseStatus.EN_AJUSTES]


# ==========================
# Documentos asociados a Case
# ==========================

class DocumentCategory(models.TextChoices):
    IDENTIDAD = "IDENTIDAD", "Identidad"
    SOPORTE = "SOPORTE", "Soporte"
    OTRO = "OTRO", "Otro"


class CaseDocument(models.Model):
    case = models.ForeignKey("cases.Case", on_delete=models.CASCADE, related_name="documents")

    category = models.CharField(
        max_length=30,
        choices=DocumentCategory.choices,
        default=DocumentCategory.OTRO,
    )

    # ✅ Cloudinary: guardamos URL y public_id (NO FileField)
    file_url = models.URLField(max_length=500)
    public_id = models.CharField(max_length=255, blank=True, default="")

    # metadata
    original_name = models.CharField(max_length=255)
    size_bytes = models.BigIntegerField(default=0)
    mime_type = models.CharField(max_length=100, blank=True, default="")

    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
