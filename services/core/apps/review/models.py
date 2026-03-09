import uuid

from django.db import models


class ReviewAssignment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    idea_id = models.UUIDField()
    reviewer_id = models.UUIDField()
    assigned_by = models.CharField(max_length=10)
    assigned_at = models.DateTimeField(auto_now_add=True)
    unassigned_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "review_assignments"


class ReviewTimelineEntry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    idea_id = models.UUIDField()
    entry_type = models.CharField(max_length=20)
    author_id = models.UUIDField(null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    parent_entry_id = models.UUIDField(null=True, blank=True)
    old_state = models.CharField(max_length=20, null=True, blank=True)
    new_state = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "review_timeline_entries"
