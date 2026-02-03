from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.db.models import Q

class Role(models.TextChoices):
    ADMIN = "ADMIN", "Administrador"
    GESTOR = "GESTOR", "Gestor"
    CAMPESINO = "CAMPESINO", "Campesino"
    ASOCIACION = "ASOCIACION", "Asociación"

class DocumentType(models.TextChoices):
    CC = "CC", "Cédula"
    TI = "TI", "Tarjeta de identidad"
    CE = "CE", "Cédula extranjería"
    NIT = "NIT", "NIT"

class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El email es obligatorio")
        email = self.normalize_email(email)

        # compatibilidad: si viene document_number y no document_id, lo copiamos
        doc_number = extra_fields.get("document_number")
        if doc_number and not extra_fields.get("document_id"):
            extra_fields["document_id"] = doc_number

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", Role.ADMIN)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser debe tener is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser debe tener is_superuser=True.")
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    role = models.CharField(max_length=20, choices=Role.choices)
    phone = models.CharField(max_length=30, blank=True, default="")

    # legado (lo mantenemos)
    document_id = models.CharField(max_length=50, blank=True, default="")

    # ✅ nuevos campos para cumplir login por tipo + número
    document_type = models.CharField(max_length=10, choices=DocumentType.choices, null=True, blank=True)
    document_number = models.CharField(max_length=30, null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["document_type", "document_number"],
                condition=Q(document_type__isnull=False) & Q(document_number__isnull=False),
                name="uniq_document_type_number",
            )
        ]
