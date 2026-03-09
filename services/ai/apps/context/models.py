import uuid

from django.db import models


class ChatContextSummary(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    idea_id = models.UUIDField()
    summary_text = models.TextField()
    messages_covered_up_to_id = models.UUIDField()
    compression_iteration = models.IntegerField(default=1)
    context_window_usage_at_compression = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "chat_context_summaries"
        indexes = [
            models.Index(fields=["idea_id"], name="idx_ctx_summary_idea"),
        ]


class FacilitatorContextBucket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.TextField(default="")
    updated_by = models.UUIDField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "facilitator_context_bucket"


class ContextAgentBucket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sections = models.JSONField(default=dict)
    free_text = models.TextField(default="")
    updated_by = models.UUIDField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "context_agent_bucket"
