import uuid

from django.db import models


class RequirementsDocumentDraft(models.Model):
    """Unmanaged mirror model — reads Core service's requirements_document_drafts table."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project_id = models.UUIDField(unique=True)
    title = models.TextField(null=True, blank=True)
    short_description = models.TextField(null=True, blank=True)
    structure = models.JSONField(default=list)
    item_locks = models.JSONField(default=dict)
    allow_information_gaps = models.BooleanField(default=False)
    readiness_evaluation = models.JSONField(default=dict)
    last_evaluated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = "requirements_document_drafts"

    def __str__(self) -> str:
        return f"RequirementsDocumentDraft for project {self.project_id}"


# Backwards-compatible alias for code that still references BrdDraft
BrdDraft = RequirementsDocumentDraft
