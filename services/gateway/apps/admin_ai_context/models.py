import uuid

from django.db import models


class FacilitatorContextBucket(models.Model):
    """Unmanaged mirror — reads AI service's facilitator_context_bucket table."""

    CONTEXT_TYPE_CHOICES = [
        ("global", "Global"),
        ("software", "Software"),
        ("non_software", "Non-Software"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    context_type = models.CharField(
        max_length=20,
        choices=CONTEXT_TYPE_CHOICES,
        default="global",
        unique=True,
    )
    content = models.TextField(default="")
    updated_by = models.UUIDField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = "facilitator_context_bucket"


class ContextAgentBucket(models.Model):
    """Unmanaged mirror — reads AI service's context_agent_bucket table."""

    CONTEXT_TYPE_CHOICES = [
        ("global", "Global"),
        ("software", "Software"),
        ("non_software", "Non-Software"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    context_type = models.CharField(
        max_length=20,
        choices=CONTEXT_TYPE_CHOICES,
        default="global",
        unique=True,
    )
    sections = models.JSONField(default=dict)
    free_text = models.TextField(default="")
    updated_by = models.UUIDField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = "context_agent_bucket"
