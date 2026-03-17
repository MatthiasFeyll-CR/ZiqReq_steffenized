import uuid

from django.core.exceptions import ValidationError
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


# --- Structure validation helpers ---

VALID_SOFTWARE_PARENT_TYPE = "epic"
VALID_SOFTWARE_CHILD_TYPE = "user_story"
VALID_NON_SOFTWARE_PARENT_TYPE = "milestone"
VALID_NON_SOFTWARE_CHILD_TYPE = "work_package"


def validate_structure(structure: list, project_type: str) -> None:
    """Validate hierarchical requirements structure against project_type."""
    if not isinstance(structure, list):
        raise ValidationError("Structure must be a list.")

    if project_type == "software":
        parent_type = VALID_SOFTWARE_PARENT_TYPE
        child_type = VALID_SOFTWARE_CHILD_TYPE
    elif project_type == "non_software":
        parent_type = VALID_NON_SOFTWARE_PARENT_TYPE
        child_type = VALID_NON_SOFTWARE_CHILD_TYPE
    else:
        raise ValidationError(f"Invalid project_type: {project_type}")

    for item in structure:
        if not isinstance(item, dict):
            raise ValidationError("Each top-level item must be a dict.")
        if item.get("type") != parent_type:
            raise ValidationError(
                f"Top-level items must have type='{parent_type}' "
                f"for {project_type} projects, got '{item.get('type')}'."
            )
        if "id" not in item:
            raise ValidationError("Each item must have an 'id' field.")
        children = item.get("children", [])
        if not isinstance(children, list):
            raise ValidationError("'children' must be a list.")
        for child in children:
            if not isinstance(child, dict):
                raise ValidationError("Each child must be a dict.")
            if child.get("type") != child_type:
                raise ValidationError(
                    f"Children must have type='{child_type}' "
                    f"for {project_type} projects, got '{child.get('type')}'."
                )
            if "id" not in child:
                raise ValidationError("Each child must have an 'id' field.")


class RequirementsDocumentDraft(models.Model):
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
        db_table = "requirements_document_drafts"

    def clean(self) -> None:
        if self.structure:
            validate_structure(self.structure, self.project.project_type)

    def __str__(self) -> str:
        return f"RequirementsDocumentDraft for project {self.project_id}"


class RequirementsDocumentVersion(models.Model):
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
        db_table = "requirements_document_versions"
        unique_together = [("project", "version_number")]
        indexes = [
            models.Index(
                fields=["project", "version_number"],
                name="idx_req_ver_project",
            ),
        ]

    def save(self, *args, **kwargs):  # type: ignore[override]
        if not self._state.adding:
            raise ValidationError(
                "RequirementsDocumentVersion is immutable and cannot be updated."
            )
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"RequirementsDocumentVersion {self.version_number} for project {self.project_id}"
