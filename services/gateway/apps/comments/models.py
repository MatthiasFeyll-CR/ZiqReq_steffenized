import uuid

from django.db import models


class IdeaComment(models.Model):
    """A comment or system event entry on an idea's comment timeline."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    idea_id = models.UUIDField(db_index=True)
    author_id = models.UUIDField(null=True, blank=True)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="replies",
    )
    content = models.TextField()
    is_system_event = models.BooleanField(default=False)
    system_event_type = models.CharField(max_length=50, null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "idea_comments"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["idea_id", "created_at"], name="idx_comments_idea_ts"),
        ]

    def __str__(self) -> str:
        if self.is_system_event:
            return f"SystemEvent {self.system_event_type} on idea {self.idea_id}"
        return f"Comment {self.id} by {self.author_id}"


class CommentReaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    comment = models.ForeignKey(
        IdeaComment,
        on_delete=models.CASCADE,
        related_name="reactions",
    )
    user_id = models.UUIDField()
    emoji = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "comment_reactions"
        unique_together = [("comment", "user_id", "emoji")]

    def __str__(self) -> str:
        return f"{self.emoji} by {self.user_id} on {self.comment_id}"


class CommentReadStatus(models.Model):
    """Tracks when a user last read the comment section for an idea."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    idea_id = models.UUIDField()
    user_id = models.UUIDField()
    last_read_at = models.DateTimeField()

    class Meta:
        db_table = "comment_read_status"
        unique_together = [("idea_id", "user_id")]

    def __str__(self) -> str:
        return f"ReadStatus user={self.user_id} idea={self.idea_id}"
