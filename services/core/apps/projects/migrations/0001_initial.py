import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Idea",
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
                ("owner_id", models.UUIDField()),
                ("co_owner_id", models.UUIDField(blank=True, null=True)),
                ("share_link_token", models.CharField(blank=True, max_length=64, null=True, unique=True)),
                ("merged_from_idea_1_id", models.UUIDField(blank=True, null=True)),
                ("merged_from_idea_2_id", models.UUIDField(blank=True, null=True)),
                ("closed_by_merge_id", models.UUIDField(blank=True, null=True)),
                ("closed_by_append_id", models.UUIDField(blank=True, null=True)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "ideas",
            },
        ),
        migrations.CreateModel(
            name="IdeaCollaborator",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("user_id", models.UUIDField()),
                ("joined_at", models.DateTimeField(auto_now_add=True)),
                (
                    "idea",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="collaborators",
                        to="ideas.idea",
                    ),
                ),
            ],
            options={
                "db_table": "idea_collaborators",
                "unique_together": {("idea", "user_id")},
            },
        ),
        # Idea indexes
        migrations.AddIndex(
            model_name="idea",
            index=models.Index(fields=["owner_id"], name="idx_ideas_owner"),
        ),
        migrations.AddIndex(
            model_name="idea",
            index=models.Index(fields=["co_owner_id"], name="idx_ideas_co_owner"),
        ),
        migrations.AddIndex(
            model_name="idea",
            index=models.Index(fields=["state"], name="idx_ideas_state"),
        ),
        migrations.AddIndex(
            model_name="idea",
            index=models.Index(fields=["deleted_at"], name="idx_ideas_deleted_at"),
        ),
        migrations.AddIndex(
            model_name="idea",
            index=models.Index(fields=["state", "deleted_at"], name="idx_ideas_state_deleted"),
        ),
        # IdeaCollaborator indexes
        migrations.AddIndex(
            model_name="ideacollaborator",
            index=models.Index(fields=["user_id"], name="idx_collab_user"),
        ),
        migrations.AddIndex(
            model_name="ideacollaborator",
            index=models.Index(fields=["idea"], name="idx_collab_idea"),
        ),
        # CHECK constraints via raw SQL
        migrations.RunSQL(
            sql=[
                (
                    "ALTER TABLE ideas ADD CONSTRAINT chk_ideas_state"
                    " CHECK (state IN"
                    " ('open','in_review','accepted','dropped','rejected'));"
                ),
                (
                    "ALTER TABLE ideas ADD CONSTRAINT chk_ideas_visibility"
                    " CHECK (visibility IN ('private','collaborating'));"
                ),
                (
                    "ALTER TABLE ideas ADD CONSTRAINT chk_ideas_agent_mode"
                    " CHECK (agent_mode IN ('interactive','silent'));"
                ),
            ],
            reverse_sql=[
                "ALTER TABLE ideas DROP CONSTRAINT IF EXISTS chk_ideas_state;",
                "ALTER TABLE ideas DROP CONSTRAINT IF EXISTS chk_ideas_visibility;",
                "ALTER TABLE ideas DROP CONSTRAINT IF EXISTS chk_ideas_agent_mode;",
            ],
        ),
    ]
