import uuid

from django.core.exceptions import ValidationError
from django.db import models


class BrdDraft(models.Model):
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
        db_table = "brd_drafts"

    def __str__(self) -> str:
        return f"BrdDraft for idea {self.idea_id}"


class BrdVersion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    idea_id = models.UUIDField()
    version_number = models.IntegerField()
    section_title = models.TextField(null=True, blank=True)
    section_short_description = models.TextField(null=True, blank=True)
    section_current_workflow = models.TextField(null=True, blank=True)
    section_affected_department = models.TextField(null=True, blank=True)
    section_core_capabilities = models.TextField(null=True, blank=True)
    section_success_criteria = models.TextField(null=True, blank=True)
    pdf_file_path = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "brd_versions"
        unique_together = [("idea_id", "version_number")]
        indexes = [
            models.Index(fields=["idea_id", "version_number"], name="idx_brd_ver_idea"),
        ]

    def save(self, *args, **kwargs):  # type: ignore[override]
        if not self._state.adding:
            raise ValidationError("BrdVersion is immutable and cannot be updated.")
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"BrdVersion {self.version_number} for idea {self.idea_id}"
