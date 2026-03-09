import uuid

from django.db import models


class IdeaKeywords(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    idea_id = models.UUIDField(unique=True)
    keywords = models.JSONField(default=list)
    last_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "idea_keywords"


class MergeRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    requesting_idea_id = models.UUIDField()
    target_idea_id = models.UUIDField()
    merge_type = models.CharField(max_length=10)
    requested_by = models.UUIDField()
    status = models.CharField(max_length=15, default="pending")
    requesting_owner_consent = models.CharField(max_length=15, default="accepted")
    target_owner_consent = models.CharField(max_length=15, default="pending")
    reviewer_consent = models.CharField(max_length=20, default="not_required")
    resulting_idea_id = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "merge_requests"
