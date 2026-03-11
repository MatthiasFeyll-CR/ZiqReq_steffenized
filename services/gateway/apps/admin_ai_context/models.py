import uuid

from django.db import models


class FacilitatorContextBucket(models.Model):
    """Unmanaged mirror — reads AI service's facilitator_context_bucket table."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.TextField(default="")
    updated_by = models.UUIDField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = "facilitator_context_bucket"


class ContextAgentBucket(models.Model):
    """Unmanaged mirror — reads AI service's context_agent_bucket table."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sections = models.JSONField(default=dict)
    free_text = models.TextField(default="")
    updated_by = models.UUIDField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = "context_agent_bucket"
