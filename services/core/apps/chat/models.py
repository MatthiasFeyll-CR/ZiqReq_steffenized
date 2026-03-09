import uuid

from django.db import models


class ChatMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    idea_id = models.UUIDField()
    sender_type = models.CharField(max_length=10)
    sender_id = models.UUIDField(null=True, blank=True)
    ai_agent = models.CharField(max_length=30, null=True, blank=True)
    content = models.TextField()
    message_type = models.CharField(max_length=20, default="regular")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "chat_messages"


class AiReaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    message = models.OneToOneField(ChatMessage, on_delete=models.CASCADE)
    reaction_type = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ai_reactions"


class UserReaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE)
    user_id = models.UUIDField()
    reaction_type = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_reactions"
        unique_together = [("message", "user_id")]
