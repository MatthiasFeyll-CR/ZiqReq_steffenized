import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ReviewAssignment",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("project_id", models.UUIDField()),
                ("reviewer_id", models.UUIDField()),
                (
                    "assigned_by",
                    models.CharField(
                        choices=[("submitter", "Submitter"), ("self", "Self")],
                        max_length=10,
                    ),
                ),
                ("assigned_at", models.DateTimeField(auto_now_add=True)),
                ("unassigned_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "db_table": "review_assignments",
            },
        ),
        migrations.CreateModel(
            name="ReviewTimelineEntry",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("project_id", models.UUIDField()),
                (
                    "entry_type",
                    models.CharField(
                        choices=[
                            ("comment", "Comment"),
                            ("state_change", "State Change"),
                            ("resubmission", "Resubmission"),
                        ],
                        max_length=20,
                    ),
                ),
                ("author_id", models.UUIDField(blank=True, null=True)),
                ("content", models.TextField(blank=True, null=True)),
                ("parent_entry_id", models.UUIDField(blank=True, null=True)),
                ("old_state", models.CharField(blank=True, max_length=20, null=True)),
                ("new_state", models.CharField(blank=True, max_length=20, null=True)),
                ("old_version_id", models.UUIDField(blank=True, null=True)),
                ("new_version_id", models.UUIDField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "db_table": "review_timeline_entries",
            },
        ),
        # ReviewAssignment indexes
        migrations.AddIndex(
            model_name="reviewassignment",
            index=models.Index(fields=["reviewer_id", "unassigned_at"], name="idx_review_reviewer"),
        ),
        migrations.AddIndex(
            model_name="reviewassignment",
            index=models.Index(fields=["project_id"], name="idx_review_project"),
        ),
        # ReviewTimelineEntry indexes
        migrations.AddIndex(
            model_name="reviewtimelineentry",
            index=models.Index(fields=["project_id", "created_at"], name="idx_timeline_project"),
        ),
        migrations.AddIndex(
            model_name="reviewtimelineentry",
            index=models.Index(fields=["parent_entry_id"], name="idx_timeline_parent"),
        ),
        # CHECK constraints
        migrations.RunSQL(
            sql=[
                (
                    "ALTER TABLE review_assignments"
                    " ADD CONSTRAINT chk_review_assigned_by"
                    " CHECK (assigned_by IN ('submitter','self'));"
                ),
                (
                    "ALTER TABLE review_timeline_entries"
                    " ADD CONSTRAINT chk_timeline_entry_type"
                    " CHECK (entry_type IN"
                    " ('comment','state_change','resubmission'));"
                ),
            ],
            reverse_sql=[
                "ALTER TABLE review_assignments DROP CONSTRAINT IF EXISTS chk_review_assigned_by;",
                "ALTER TABLE review_timeline_entries DROP CONSTRAINT IF EXISTS chk_timeline_entry_type;",
            ],
        ),
        # Partial unique index for active review assignments
        migrations.RunSQL(
            sql=[
                (
                    "CREATE UNIQUE INDEX uq_active_review_assignment"
                    " ON review_assignments (project_id, reviewer_id)"
                    " WHERE unassigned_at IS NULL;"
                ),
            ],
            reverse_sql=[
                "DROP INDEX IF EXISTS uq_active_review_assignment;",
            ],
        ),
    ]
