import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Project",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("title", models.CharField(default="", max_length=500)),
                ("title_manually_edited", models.BooleanField(default=False)),
                (
                    "state",
                    models.CharField(
                        choices=[
                            ("open", "Open"),
                            ("in_review", "In Review"),
                            ("accepted", "Accepted"),
                            ("dropped", "Dropped"),
                            ("rejected", "Rejected"),
                        ],
                        default="open",
                        max_length=20,
                    ),
                ),
                (
                    "visibility",
                    models.CharField(
                        choices=[("private", "Private"), ("collaborating", "Collaborating")],
                        default="private",
                        max_length=20,
                    ),
                ),
                (
                    "agent_mode",
                    models.CharField(
                        choices=[("interactive", "Interactive"), ("silent", "Silent")],
                        default="interactive",
                        max_length=20,
                    ),
                ),
                (
                    "project_type",
                    models.CharField(
                        choices=[("software", "Software"), ("non_software", "Non-Software")],
                        default="software",
                        max_length=20,
                    ),
                ),
                ("owner_id", models.UUIDField()),
                ("share_link_token", models.CharField(blank=True, max_length=64, null=True, unique=True)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "projects",
            },
        ),
        migrations.CreateModel(
            name="ProjectCollaborator",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("user_id", models.UUIDField()),
                ("joined_at", models.DateTimeField(auto_now_add=True)),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="collaborators",
                        to="projects.project",
                    ),
                ),
            ],
            options={
                "db_table": "project_collaborators",
                "unique_together": {("project", "user_id")},
            },
        ),
        # Project indexes
        migrations.AddIndex(
            model_name="project",
            index=models.Index(fields=["owner_id"], name="idx_projects_owner"),
        ),
        migrations.AddIndex(
            model_name="project",
            index=models.Index(fields=["state"], name="idx_projects_state"),
        ),
        migrations.AddIndex(
            model_name="project",
            index=models.Index(fields=["deleted_at"], name="idx_projects_deleted_at"),
        ),
        migrations.AddIndex(
            model_name="project",
            index=models.Index(fields=["state", "deleted_at"], name="idx_projects_state_deleted"),
        ),
        migrations.AddIndex(
            model_name="project",
            index=models.Index(fields=["project_type"], name="idx_projects_type"),
        ),
        # ProjectCollaborator indexes
        migrations.AddIndex(
            model_name="projectcollaborator",
            index=models.Index(fields=["user_id"], name="idx_collab_user"),
        ),
        migrations.AddIndex(
            model_name="projectcollaborator",
            index=models.Index(fields=["project"], name="idx_collab_project"),
        ),
        # CHECK constraints via raw SQL
        migrations.RunSQL(
            sql=[
                (
                    "ALTER TABLE projects ADD CONSTRAINT chk_projects_state"
                    " CHECK (state IN"
                    " ('open','in_review','accepted','dropped','rejected'));"
                ),
                (
                    "ALTER TABLE projects ADD CONSTRAINT chk_projects_visibility"
                    " CHECK (visibility IN ('private','collaborating'));"
                ),
                (
                    "ALTER TABLE projects ADD CONSTRAINT chk_projects_agent_mode"
                    " CHECK (agent_mode IN ('interactive','silent'));"
                ),
                (
                    "ALTER TABLE projects ADD CONSTRAINT chk_projects_project_type"
                    " CHECK (project_type IN ('software','non_software'));"
                ),
            ],
            reverse_sql=[
                "ALTER TABLE projects DROP CONSTRAINT IF EXISTS chk_projects_state;",
                "ALTER TABLE projects DROP CONSTRAINT IF EXISTS chk_projects_visibility;",
                "ALTER TABLE projects DROP CONSTRAINT IF EXISTS chk_projects_agent_mode;",
                "ALTER TABLE projects DROP CONSTRAINT IF EXISTS chk_projects_project_type;",
            ],
        ),
    ]
