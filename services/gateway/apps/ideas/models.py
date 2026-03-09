import uuid

from django.db import models


class Idea(models.Model):
    STATE_CHOICES = [
        ("open", "Open"),
        ("in_review", "In Review"),
        ("accepted", "Accepted"),
        ("dropped", "Dropped"),
        ("rejected", "Rejected"),
    ]
    VISIBILITY_CHOICES = [
        ("private", "Private"),
        ("collaborating", "Collaborating"),
    ]
    AGENT_MODE_CHOICES = [
        ("interactive", "Interactive"),
        ("silent", "Silent"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=500, default="")
    title_manually_edited = models.BooleanField(default=False)
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default="open")
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default="private")
    agent_mode = models.CharField(max_length=20, choices=AGENT_MODE_CHOICES, default="interactive")
    owner_id = models.UUIDField()
    co_owner_id = models.UUIDField(null=True, blank=True)
    share_link_token = models.CharField(max_length=64, null=True, blank=True, unique=True)
    merged_from_idea_1_id = models.UUIDField(null=True, blank=True)
    merged_from_idea_2_id = models.UUIDField(null=True, blank=True)
    closed_by_merge_id = models.UUIDField(null=True, blank=True)
    closed_by_append_id = models.UUIDField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ideas"

    def __str__(self) -> str:
        return self.title or f"Idea {self.id}"


class IdeaCollaborator(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name="collaborators")
    user_id = models.UUIDField()
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "idea_collaborators"
        unique_together = [("idea", "user_id")]

    def __str__(self) -> str:
        return f"Collaborator {self.user_id} on {self.idea_id}"


class ChatMessage(models.Model):
    SENDER_TYPE_CHOICES = [
        ("user", "User"),
        ("ai", "AI"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    idea_id = models.UUIDField()
    sender_type = models.CharField(max_length=10, choices=SENDER_TYPE_CHOICES)
    sender_id = models.UUIDField(null=True, blank=True)
    ai_agent = models.CharField(max_length=30, null=True, blank=True)
    content = models.TextField()
    message_type = models.CharField(max_length=20, default="regular")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "chat_messages"

    def __str__(self) -> str:
        return f"ChatMessage {self.id} ({self.sender_type})"
