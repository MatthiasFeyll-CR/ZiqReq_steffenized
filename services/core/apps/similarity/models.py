import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models


class IdeaKeywords(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    idea_id = models.UUIDField(unique=True)
    keywords = ArrayField(models.CharField(max_length=100), default=list)
    last_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "idea_keywords"


class MergeRequest(models.Model):
    MERGE_TYPE_CHOICES = [
        ("merge", "Merge"),
        ("append", "Append"),
    ]
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("declined", "Declined"),
    ]
    CONSENT_CHOICES = [
        ("accepted", "Accepted"),
        ("pending", "Pending"),
    ]
    TARGET_CONSENT_CHOICES = [
        ("accepted", "Accepted"),
        ("pending", "Pending"),
        ("declined", "Declined"),
    ]
    REVIEWER_CONSENT_CHOICES = [
        ("accepted", "Accepted"),
        ("pending", "Pending"),
        ("declined", "Declined"),
        ("not_required", "Not Required"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    requesting_idea_id = models.UUIDField()
    target_idea_id = models.UUIDField()
    merge_type = models.CharField(max_length=10, choices=MERGE_TYPE_CHOICES)
    requested_by = models.UUIDField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="pending")
    requesting_owner_consent = models.CharField(max_length=15, choices=CONSENT_CHOICES, default="accepted")
    target_owner_consent = models.CharField(max_length=15, choices=TARGET_CONSENT_CHOICES, default="pending")
    reviewer_consent = models.CharField(max_length=20, choices=REVIEWER_CONSENT_CHOICES, default="not_required")
    resulting_idea_id = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "merge_requests"
        indexes = [
            models.Index(fields=["target_idea_id", "status"], name="idx_merge_target"),
            models.Index(fields=["requesting_idea_id", "status"], name="idx_merge_requesting"),
        ]
