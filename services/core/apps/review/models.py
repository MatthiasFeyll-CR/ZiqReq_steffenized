import uuid

from django.core.exceptions import ValidationError
from django.db import models


class ReviewAssignment(models.Model):
    ASSIGNED_BY_CHOICES = [
        ("submitter", "Submitter"),
        ("self", "Self"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project_id = models.UUIDField()
    reviewer_id = models.UUIDField()
    assigned_by = models.CharField(max_length=10, choices=ASSIGNED_BY_CHOICES)
    assigned_at = models.DateTimeField(auto_now_add=True)
    unassigned_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "review_assignments"
        indexes = [
            models.Index(fields=["reviewer_id", "unassigned_at"], name="idx_review_reviewer"),
            models.Index(fields=["project_id"], name="idx_review_project"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["project_id", "reviewer_id"],
                condition=models.Q(unassigned_at__isnull=True),
                name="uq_active_review_assignment",
            ),
        ]

    def __str__(self) -> str:
        return f"ReviewAssignment {self.reviewer_id} on project {self.project_id}"


class ReviewTimelineEntry(models.Model):
    ENTRY_TYPE_CHOICES = [
        ("comment", "Comment"),
        ("state_change", "State Change"),
        ("resubmission", "Resubmission"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project_id = models.UUIDField()
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
        db_table = "review_timeline_entries"
        indexes = [
            models.Index(fields=["project_id", "created_at"], name="idx_timeline_project"),
            models.Index(fields=["parent_entry_id"], name="idx_timeline_parent"),
        ]

    def save(self, *args, **kwargs):  # type: ignore[override]
        if not self._state.adding:
            raise ValidationError("ReviewTimelineEntry is immutable and cannot be updated.")
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"TimelineEntry {self.entry_type} on project {self.project_id}"
