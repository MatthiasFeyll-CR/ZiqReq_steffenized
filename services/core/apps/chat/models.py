import uuid

from django.core.exceptions import ValidationError
from django.db import models


class ChatMessage(models.Model):
    SENDER_TYPE_CHOICES = [
        ("user", "User"),
        ("ai", "AI"),
    ]
    MESSAGE_TYPE_CHOICES = [
        ("regular", "Regular"),
        ("delegation", "Delegation"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project_id = models.UUIDField()
    sender_type = models.CharField(max_length=10, choices=SENDER_TYPE_CHOICES)
    sender_id = models.UUIDField(null=True, blank=True)
    ai_agent = models.CharField(max_length=30, null=True, blank=True)
    content = models.TextField()
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, default="regular")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "chat_messages"
        indexes = [
            models.Index(fields=["project_id", "created_at"], name="idx_chat_project_created"),
            models.Index(fields=["sender_id"], name="idx_chat_sender"),
        ]

    def save(self, *args, **kwargs):  # type: ignore[override]
        if not self._state.adding:
            raise ValidationError("ChatMessage is immutable and cannot be updated.")
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"ChatMessage {self.id} ({self.sender_type})"


class AiReaction(models.Model):
    REACTION_TYPE_CHOICES = [
        ("thumbs_up", "Thumbs Up"),
        ("thumbs_down", "Thumbs Down"),
        ("heart", "Heart"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.OneToOneField(ChatMessage, on_delete=models.CASCADE)
    reaction_type = models.CharField(max_length=15, choices=REACTION_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ai_reactions"

    def __str__(self) -> str:
        return f"AiReaction {self.reaction_type} on {self.message_id}"


class UserReaction(models.Model):
    REACTION_TYPE_CHOICES = [
        ("thumbs_up", "Thumbs Up"),
        ("thumbs_down", "Thumbs Down"),
        ("heart", "Heart"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE)
    user_id = models.UUIDField()
    reaction_type = models.CharField(max_length=15, choices=REACTION_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_reactions"
        unique_together = [("message", "user_id")]

    def __str__(self) -> str:
        return f"UserReaction {self.reaction_type} by {self.user_id}"
