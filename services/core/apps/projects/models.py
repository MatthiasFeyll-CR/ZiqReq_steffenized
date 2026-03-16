import uuid

from django.db import models


class Project(models.Model):
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
    PROJECT_TYPE_CHOICES = [
        ("software", "Software"),
        ("non_software", "Non-Software"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=500, default="")
    title_manually_edited = models.BooleanField(default=False)
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default="open")
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default="private")
    agent_mode = models.CharField(max_length=20, choices=AGENT_MODE_CHOICES, default="interactive")
    project_type = models.CharField(max_length=20, choices=PROJECT_TYPE_CHOICES, default="software")
    owner_id = models.UUIDField()
    share_link_token = models.CharField(max_length=64, null=True, blank=True, unique=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "projects"
        indexes = [
            models.Index(fields=["owner_id"], name="idx_projects_owner"),
            models.Index(fields=["state"], name="idx_projects_state"),
            models.Index(fields=["deleted_at"], name="idx_projects_deleted_at"),
            models.Index(fields=["state", "deleted_at"], name="idx_projects_state_deleted"),
            models.Index(fields=["project_type"], name="idx_projects_type"),
        ]

    def __str__(self) -> str:
        return self.title or f"Project {self.id}"


class ProjectCollaborator(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="collaborators")
    user_id = models.UUIDField()
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "project_collaborators"
        unique_together = [("project", "user_id")]
        indexes = [
            models.Index(fields=["user_id"], name="idx_collab_user"),
            models.Index(fields=["project"], name="idx_collab_project"),
        ]

    def __str__(self) -> str:
        return f"Collaborator {self.user_id} on {self.project_id}"
