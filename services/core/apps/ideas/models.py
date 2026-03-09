import uuid

from django.db import models


class Idea(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    title = models.CharField(max_length=500, default="")
    title_manually_edited = models.BooleanField(default=False)
    state = models.CharField(max_length=20, default="open")
    visibility = models.CharField(max_length=20, default="private")
    agent_mode = models.CharField(max_length=20, default="interactive")
    owner_id = models.UUIDField()
    co_owner_id = models.UUIDField(null=True, blank=True)
    share_link_token = models.CharField(max_length=64, null=True, blank=True, unique=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ideas"


class IdeaCollaborator(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name="collaborators")
    user_id = models.UUIDField()
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "idea_collaborators"
        unique_together = [("idea", "user_id")]
