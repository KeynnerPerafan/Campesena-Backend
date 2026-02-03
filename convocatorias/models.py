from django.db import models

class ConvocatoriaStatus(models.TextChoices):
    ABIERTA = "ABIERTA", "Abierta"
    CERRADA = "CERRADA", "Cerrada"

class Convocatoria(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")

    start_date = models.DateField()
    end_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=ConvocatoriaStatus.choices,
        default=ConvocatoriaStatus.ABIERTA,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        # Validar fechas (start <= end)
        if self.start_date and self.end_date and self.start_date > self.end_date:
            from django.core.exceptions import ValidationError
            raise ValidationError("start_date no puede ser mayor que end_date")
