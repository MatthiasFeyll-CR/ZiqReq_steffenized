from django.db import models

import uuid


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user_id = models.UUIDField()
    event_type = models.CharField(max_length=50)
    title = models.CharField(max_length=300)
    body = models.TextField()
    reference_id = models.UUIDField(null=True, blank=True)
    reference_type = models.CharField(max_length=30, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    action_taken = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notifications"
