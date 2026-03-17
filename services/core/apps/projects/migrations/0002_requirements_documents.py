"""Create requirements_document_drafts and requirements_document_versions tables.

Migrates data from brd_drafts/brd_versions into the new hierarchical structure,
then drops the old BRD tables.
"""

import uuid

import django.db.models.deletion
from django.db import migrations, models


def migrate_brd_to_requirements(apps, schema_editor):
    """Migrate existing brd_drafts rows into requirements_document_drafts."""
    with schema_editor.connection.cursor() as cursor:
        # Check if brd_drafts table exists
        cursor.execute(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'brd_drafts')"
        )
        if not cursor.fetchone()[0]:
            return

        # Detect column name: idea_id (fresh DB) or project_id (already renamed)
        cursor.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'brd_drafts' AND column_name IN ('project_id', 'idea_id')"
        )
        fk_col = cursor.fetchone()[0]

        # Fetch all brd_drafts
        cursor.execute(
            f"SELECT id, {fk_col}, section_title, section_short_description, "
            "section_current_workflow, section_affected_department, "
            "section_core_capabilities, section_success_criteria, "
            "section_locks, allow_information_gaps, readiness_evaluation, "
            "last_evaluated_at, created_at, updated_at "
            "FROM brd_drafts"
        )
        drafts = cursor.fetchall()

        for row in drafts:
            (
                draft_id, project_id, title, short_desc,
                current_workflow, affected_dept,
                core_caps, success_criteria,
                section_locks, allow_gaps, readiness_eval,
                last_eval_at, created_at, updated_at,
            ) = row

            # Look up project_type
            cursor.execute(
                "SELECT project_type FROM projects WHERE id = %s", [project_id]
            )
            project_row = cursor.fetchone()
            if not project_row:
                continue
            project_type = project_row[0]

            # Convert flat BRD sections into a single parent item with description
            sections_text = "\n\n".join(
                filter(None, [current_workflow, affected_dept, core_caps, success_criteria])
            )

            if project_type == "non_software":
                parent_type = "milestone"
            else:
                parent_type = "epic"

            # Build structure: one parent item containing BRD content
            import json

            structure = []
            if sections_text or title or short_desc:
                parent_id = str(uuid.uuid4())
                structure = [
                    {
                        "id": parent_id,
                        "type": parent_type,
                        "title": title or "Imported from BRD",
                        "description": sections_text,
                        "children": [],
                        "metadata": {"migrated_from_brd": True},
                    }
                ]

            # Convert section_locks to item_locks (empty since new structure has new IDs)
            item_locks = {}

            cursor.execute(
                "INSERT INTO requirements_document_drafts "
                "(id, project_id, title, short_description, structure, item_locks, "
                "allow_information_gaps, readiness_evaluation, last_evaluated_at, "
                "created_at, updated_at) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                [
                    str(uuid.uuid4()),
                    str(project_id),
                    title,
                    short_desc,
                    json.dumps(structure),
                    json.dumps(item_locks),
                    allow_gaps,
                    json.dumps(readiness_eval) if isinstance(readiness_eval, dict) else readiness_eval or "{}",
                    last_eval_at,
                    created_at,
                    updated_at,
                ],
            )

        # Migrate brd_versions
        cursor.execute(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'brd_versions')"
        )
        if cursor.fetchone()[0]:
            # Detect column name for brd_versions too
            cursor.execute(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name = 'brd_versions' AND column_name IN ('project_id', 'idea_id')"
            )
            ver_fk_col = cursor.fetchone()[0]

            cursor.execute(
                f"SELECT id, {ver_fk_col}, version_number, section_title, "
                "section_short_description, section_current_workflow, "
                "section_affected_department, section_core_capabilities, "
                "section_success_criteria, pdf_file_path, created_at "
                "FROM brd_versions"
            )
            versions = cursor.fetchall()

            for vrow in versions:
                (
                    ver_id, project_id, version_number, title, short_desc,
                    current_workflow, affected_dept, core_caps, success_criteria,
                    pdf_path, created_at,
                ) = vrow

                cursor.execute(
                    "SELECT project_type FROM projects WHERE id = %s", [project_id]
                )
                project_row = cursor.fetchone()
                project_type = project_row[0] if project_row else "software"

                sections_text = "\n\n".join(
                    filter(None, [current_workflow, affected_dept, core_caps, success_criteria])
                )

                if project_type == "non_software":
                    parent_type = "milestone"
                else:
                    parent_type = "epic"

                structure = []
                if sections_text or title or short_desc:
                    structure = [
                        {
                            "id": str(uuid.uuid4()),
                            "type": parent_type,
                            "title": title or "Imported from BRD",
                            "description": sections_text,
                            "children": [],
                            "metadata": {"migrated_from_brd": True},
                        }
                    ]

                cursor.execute(
                    "INSERT INTO requirements_document_versions "
                    "(id, project_id, version_number, title, short_description, "
                    "structure, pdf_file_path, created_at) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    [
                        str(uuid.uuid4()),
                        str(project_id),
                        version_number,
                        title,
                        short_desc,
                        json.dumps(structure),
                        pdf_path,
                        created_at,
                    ],
                )


def drop_old_brd_tables(apps, schema_editor):
    """Drop brd_drafts and brd_versions tables after migration."""
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'brd_versions')"
        )
        if cursor.fetchone()[0]:
            cursor.execute("DROP TABLE brd_versions")

        cursor.execute(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'brd_drafts')"
        )
        if cursor.fetchone()[0]:
            cursor.execute("DROP TABLE brd_drafts")


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0001_initial"),
    ]

    operations = [
        # Create requirements_document_drafts table
        migrations.CreateModel(
            name="RequirementsDocumentDraft",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("title", models.TextField(blank=True, null=True)),
                ("short_description", models.TextField(blank=True, null=True)),
                ("structure", models.JSONField(default=list)),
                ("item_locks", models.JSONField(default=dict)),
                ("allow_information_gaps", models.BooleanField(default=False)),
                ("readiness_evaluation", models.JSONField(default=dict)),
                ("last_evaluated_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "project",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="requirements_draft",
                        to="projects.project",
                    ),
                ),
            ],
            options={
                "db_table": "requirements_document_drafts",
            },
        ),
        # Create requirements_document_versions table
        migrations.CreateModel(
            name="RequirementsDocumentVersion",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("version_number", models.IntegerField()),
                ("title", models.TextField(blank=True, null=True)),
                ("short_description", models.TextField(blank=True, null=True)),
                ("structure", models.JSONField(default=list)),
                ("pdf_file_path", models.CharField(blank=True, max_length=500, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="requirements_versions",
                        to="projects.project",
                    ),
                ),
            ],
            options={
                "db_table": "requirements_document_versions",
                "unique_together": {("project", "version_number")},
                "indexes": [
                    models.Index(fields=["project", "version_number"], name="idx_req_ver_project"),
                ],
            },
        ),
        # Migrate BRD data to new tables
        migrations.RunPython(
            migrate_brd_to_requirements,
            reverse_code=migrations.RunPython.noop,
        ),
        # Drop old BRD tables
        migrations.RunPython(
            drop_old_brd_tables,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
