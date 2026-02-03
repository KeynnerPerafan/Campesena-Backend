from django.conf import settings
from django.db import models

class EventType(models.TextChoices):
    CREATED = "CREATED", "Created"
    UPDATED = "UPDATED", "Updated"
    STATUS_CHANGED = "STATUS_CHANGED", "Status changed"

class CaseEvent(models.Model):
    case = models.ForeignKey("cases.Case", on_delete=models.CASCADE, related_name="events")
    event_type = models.CharField(max_length=30, choices=EventType.choices)
    from_status = models.CharField(max_length=30, blank=True, default="")
    to_status = models.CharField(max_length=30, blank=True, default="")
    payload = models.JSONField(default=dict, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
