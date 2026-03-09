import uuid

from django.db import models


class CollaborationInvitation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    idea_id = models.UUIDField()
    inviter_id = models.UUIDField()
    invitee_id = models.UUIDField()
    status = models.CharField(max_length=15, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "collaboration_invitations"
