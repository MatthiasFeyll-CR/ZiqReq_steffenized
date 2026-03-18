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
    PROJECT_TYPE_CHOICES = [
        ("software", "Software"),
        ("non_software", "Non-Software"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=500, default="")
    title_manually_edited = models.BooleanField(default=False)
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default="open")
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default="private")
    project_type = models.CharField(max_length=20, choices=PROJECT_TYPE_CHOICES, default="software")
    owner_id = models.UUIDField()
    share_link_token = models.CharField(max_length=64, null=True, blank=True, unique=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "projects"
        indexes = [
            models.Index(fields=["-updated_at"], condition=models.Q(deleted_at__isnull=True), name="idx_projects_explore"),
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

    def __str__(self) -> str:
        return f"Collaborator {self.user_id} on {self.project_id}"


class ChatMessage(models.Model):
    SENDER_TYPE_CHOICES = [
        ("user", "User"),
        ("ai", "AI"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project_id = models.UUIDField()
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


class ChatContextSummary(models.Model):
    """Unmanaged mirror — reads AI service's chat_context_summaries table."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project_id = models.UUIDField()
    summary_text = models.TextField()
    messages_covered_up_to_id = models.UUIDField()
    compression_iteration = models.IntegerField(default=1)
    context_window_usage_at_compression = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = "chat_context_summaries"


class RequirementsDocumentDraft(models.Model):
    """Unmanaged mirror — reads Core service's requirements_document_drafts table."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.OneToOneField(
        Project, on_delete=models.CASCADE, related_name="requirements_draft"
    )
    title = models.TextField(null=True, blank=True)
    short_description = models.TextField(null=True, blank=True)
    structure = models.JSONField(default=list)
    item_locks = models.JSONField(default=dict)
    allow_information_gaps = models.BooleanField(default=False)
    readiness_evaluation = models.JSONField(default=dict)
    last_evaluated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = "requirements_document_drafts"

    def __str__(self) -> str:
        return f"RequirementsDocumentDraft for project {self.project_id}"


class RequirementsDocumentVersion(models.Model):
    """Unmanaged mirror — reads Core service's requirements_document_versions table."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="requirements_versions"
    )
    version_number = models.IntegerField()
    title = models.TextField(null=True, blank=True)
    short_description = models.TextField(null=True, blank=True)
    structure = models.JSONField(default=list)
    pdf_file_path = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = "requirements_document_versions"
        unique_together = [("project", "version_number")]

    def __str__(self) -> str:
        return f"RequirementsDocumentVersion {self.version_number} for project {self.project_id}"


class ProjectFavorite(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="favorites")
    user_id = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "project_favorites"
        unique_together = [("project", "user_id")]

    def __str__(self) -> str:
        return f"Favorite {self.user_id} on {self.project_id}"


class Attachment(models.Model):
    EXTRACTION_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="attachments")
    message_id = models.UUIDField(null=True, blank=True)
    uploader_id = models.UUIDField()
    filename = models.CharField(max_length=255)
    storage_key = models.CharField(max_length=500)
    content_type = models.CharField(max_length=100)
    size_bytes = models.BigIntegerField()
    extracted_content = models.TextField(null=True, blank=True)
    extraction_status = models.CharField(
        max_length=20, choices=EXTRACTION_STATUS_CHOICES, default="pending"
    )
    thumbnail_storage_key = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "attachments"
        indexes = [
            models.Index(fields=["project"], name="idx_attachments_project"),
            models.Index(fields=["message_id"], name="idx_attachments_message"),
            models.Index(
                fields=["project", "deleted_at"],
                name="idx_attach_proj_deleted",
            ),
        ]

    def __str__(self) -> str:
        return f"Attachment {self.filename} ({self.id})"

    @classmethod
    def active_count_for_project(cls, project_id: uuid.UUID) -> int:
        return cls.objects.filter(project_id=project_id, deleted_at__isnull=True).count()


class UserReaction(models.Model):
    REACTION_TYPE_CHOICES = [
        ("thumbs_up", "Thumbs Up"),
        ("thumbs_down", "Thumbs Down"),
        ("heart", "Heart"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message_id = models.UUIDField()
    user_id = models.UUIDField()
    reaction_type = models.CharField(max_length=15, choices=REACTION_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_reactions"
        unique_together = [("message_id", "user_id")]

    def __str__(self) -> str:
        return f"Reaction {self.reaction_type} by {self.user_id} on {self.message_id}"
