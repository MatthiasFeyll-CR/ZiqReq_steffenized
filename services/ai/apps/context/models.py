import uuid

from django.db import models


class ChatContextSummary(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project_id = models.UUIDField()
    summary_text = models.TextField()
    messages_covered_up_to_id = models.UUIDField()
    compression_iteration = models.IntegerField(default=1)
    context_window_usage_at_compression = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "chat_context_summaries"
        indexes = [
            models.Index(fields=["project_id"], name="idx_ctx_summary_project"),
        ]


class FacilitatorContextBucket(models.Model):
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
        db_table = "facilitator_context_bucket"


class ContextAgentBucket(models.Model):
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
        db_table = "context_agent_bucket"
