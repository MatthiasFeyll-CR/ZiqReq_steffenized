import uuid

from django.db import models


class BrdDraft(models.Model):
    """Unmanaged mirror model — reads Core service's brd_drafts table."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    idea_id = models.UUIDField(unique=True)
    section_title = models.TextField(null=True, blank=True)
    section_short_description = models.TextField(null=True, blank=True)
    section_current_workflow = models.TextField(null=True, blank=True)
    section_affected_department = models.TextField(null=True, blank=True)
    section_core_capabilities = models.TextField(null=True, blank=True)
    section_success_criteria = models.TextField(null=True, blank=True)
    section_locks = models.JSONField(default=dict)
    allow_information_gaps = models.BooleanField(default=False)
    readiness_evaluation = models.JSONField(default=dict)
    last_evaluated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = "brd_drafts"

    def __str__(self) -> str:
        return f"BrdDraft for idea {self.idea_id}"
