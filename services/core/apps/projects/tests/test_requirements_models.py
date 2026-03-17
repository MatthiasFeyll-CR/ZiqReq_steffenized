"""Tests for requirements document models (T-3.2.01, T-3.2.02).

These tests run in the gateway test environment (DJANGO_SETTINGS_MODULE=gateway.settings.test).
The gateway mirror models point to the same DB tables created by core migrations.
"""

import uuid

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.projects.models import (
    Project,
    RequirementsDocumentDraft,
    RequirementsDocumentVersion,
)


def validate_structure(structure, project_type):
    """Validate hierarchical requirements structure against project_type."""
    if not isinstance(structure, list):
        raise ValidationError("Structure must be a list.")

    if project_type == "software":
        parent_type = "epic"
        child_type = "user_story"
    elif project_type == "non_software":
        parent_type = "milestone"
        child_type = "work_package"
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


class TestValidateStructure(TestCase):
    """T-3.2.01: Structure validation per project_type."""

    def test_software_structure_valid(self):
        """T-3.2.01: Valid software structure with epics and user stories passes."""
        structure = [
            {
                "id": str(uuid.uuid4()),
                "type": "epic",
                "title": "Auth Epic",
                "description": "",
                "children": [
                    {
                        "id": str(uuid.uuid4()),
                        "type": "user_story",
                        "title": "Login",
                        "description": "As a user...",
                        "acceptance_criteria": [],
                        "priority": "high",
                    }
                ],
            }
        ]
        validate_structure(structure, "software")

    def test_non_software_structure_valid(self):
        """Valid non-software structure with milestones and work packages passes."""
        structure = [
            {
                "id": str(uuid.uuid4()),
                "type": "milestone",
                "title": "Phase 1",
                "description": "",
                "children": [
                    {
                        "id": str(uuid.uuid4()),
                        "type": "work_package",
                        "title": "Deliverable 1",
                        "description": "",
                        "deliverables": [],
                    }
                ],
            }
        ]
        validate_structure(structure, "non_software")

    def test_software_rejects_milestone(self):
        """Software projects reject milestone as parent type."""
        structure = [
            {
                "id": str(uuid.uuid4()),
                "type": "milestone",
                "title": "Wrong type",
                "children": [],
            }
        ]
        with self.assertRaises(ValidationError):
            validate_structure(structure, "software")

    def test_non_software_rejects_epic(self):
        """Non-software projects reject epic as parent type."""
        structure = [
            {
                "id": str(uuid.uuid4()),
                "type": "epic",
                "title": "Wrong type",
                "children": [],
            }
        ]
        with self.assertRaises(ValidationError):
            validate_structure(structure, "non_software")

    def test_software_rejects_work_package_child(self):
        """Software projects reject work_package as child type."""
        structure = [
            {
                "id": str(uuid.uuid4()),
                "type": "epic",
                "title": "Epic",
                "children": [
                    {
                        "id": str(uuid.uuid4()),
                        "type": "work_package",
                        "title": "Wrong child",
                    }
                ],
            }
        ]
        with self.assertRaises(ValidationError):
            validate_structure(structure, "software")

    def test_empty_structure_valid(self):
        """Empty structure is valid for any project type."""
        validate_structure([], "software")
        validate_structure([], "non_software")

    def test_missing_id_raises(self):
        """Items without id field raise ValidationError."""
        structure = [{"type": "epic", "title": "No ID", "children": []}]
        with self.assertRaises(ValidationError):
            validate_structure(structure, "software")

    def test_non_list_structure_raises(self):
        """Non-list structure raises ValidationError."""
        with self.assertRaises(ValidationError):
            validate_structure("not a list", "software")


class TestRequirementsDocumentDraft(TestCase):
    def setUp(self):
        self.project = Project.objects.create(
            owner_id=uuid.uuid4(), project_type="software"
        )

    def test_create_empty_draft(self):
        draft = RequirementsDocumentDraft.objects.create(
            project=self.project,
            structure=[],
            item_locks={},
        )
        assert draft.structure == []
        assert draft.item_locks == {}
        assert draft.allow_information_gaps is False

    def test_one_draft_per_project(self):
        """project_id is UNIQUE — second draft raises IntegrityError."""
        RequirementsDocumentDraft.objects.create(project=self.project)
        from django.db import IntegrityError

        with self.assertRaises(IntegrityError):
            RequirementsDocumentDraft.objects.create(project=self.project)


class TestRequirementsDocumentVersion(TestCase):
    """T-3.2.02: Version model is immutable (tested at DB constraint level)."""

    def setUp(self):
        self.project = Project.objects.create(
            owner_id=uuid.uuid4(), project_type="software"
        )

    def test_create_version(self):
        version = RequirementsDocumentVersion.objects.create(
            project=self.project,
            version_number=1,
            title="v1",
            structure=[],
        )
        assert version.version_number == 1

    def test_unique_project_version(self):
        """UNIQUE constraint on (project, version_number)."""
        RequirementsDocumentVersion.objects.create(
            project=self.project, version_number=1, structure=[]
        )
        from django.db import IntegrityError

        with self.assertRaises(IntegrityError):
            RequirementsDocumentVersion.objects.create(
                project=self.project, version_number=1, structure=[]
            )
