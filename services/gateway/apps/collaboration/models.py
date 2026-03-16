import uuid

from django.db import models


class CollaborationInvitation(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("declined", "Declined"),
        ("revoked", "Revoked"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project_id = models.UUIDField()
    inviter_id = models.UUIDField()
    invitee_id = models.UUIDField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "collaboration_invitations"

    def __str__(self) -> str:
        return f"Invitation {self.status} from {self.inviter_id} to {self.invitee_id}"
