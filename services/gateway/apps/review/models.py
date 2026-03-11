import uuid

from django.core.exceptions import ValidationError
from django.db import models


class BrdVersion(models.Model):
    """Unmanaged mirror — reads Core service's brd_versions table."""

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
        managed = False
        db_table = "brd_versions"

    def __str__(self) -> str:
        return f"BrdVersion {self.version_number} for idea {self.idea_id}"


class ReviewAssignment(models.Model):
    """Unmanaged mirror — reads Core service's review_assignments table."""

    ASSIGNED_BY_CHOICES = [
        ("submitter", "Submitter"),
        ("self", "Self"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    idea_id = models.UUIDField()
    reviewer_id = models.UUIDField()
    assigned_by = models.CharField(max_length=10, choices=ASSIGNED_BY_CHOICES)
    assigned_at = models.DateTimeField(auto_now_add=True)
    unassigned_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "review_assignments"

    def __str__(self) -> str:
        return f"ReviewAssignment {self.reviewer_id} on idea {self.idea_id}"


class ReviewTimelineEntry(models.Model):
    """Unmanaged mirror — reads Core service's review_timeline_entries table."""

    ENTRY_TYPE_CHOICES = [
        ("comment", "Comment"),
        ("state_change", "State Change"),
        ("resubmission", "Resubmission"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    idea_id = models.UUIDField()
    entry_type = models.CharField(max_length=20, choices=ENTRY_TYPE_CHOICES)
    author_id = models.UUIDField(null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    parent_entry_id = models.UUIDField(null=True, blank=True)
    old_state = models.CharField(max_length=20, null=True, blank=True)
    new_state = models.CharField(max_length=20, null=True, blank=True)
    old_version_id = models.UUIDField(null=True, blank=True)
    new_version_id = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = "review_timeline_entries"

    def save(self, *args, **kwargs):  # type: ignore[override]
        if not self._state.adding:
            raise ValidationError("ReviewTimelineEntry is immutable and cannot be updated.")
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"TimelineEntry {self.entry_type} on idea {self.idea_id}"
