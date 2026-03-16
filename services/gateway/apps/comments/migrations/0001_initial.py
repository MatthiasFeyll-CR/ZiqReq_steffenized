import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ProjectComment",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("project_id", models.UUIDField(db_index=True)),
                ("author_id", models.UUIDField(blank=True, null=True)),
                ("content", models.TextField()),
                ("is_system_event", models.BooleanField(default=False)),
                ("system_event_type", models.CharField(blank=True, max_length=50, null=True)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="replies",
                        to="gateway_comments.projectcomment",
                    ),
                ),
            ],
            options={
                "db_table": "project_comments",
                "ordering": ["created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="projectcomment",
            index=models.Index(fields=["project_id", "created_at"], name="idx_comments_project_ts"),
        ),
        migrations.CreateModel(
            name="CommentReaction",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("user_id", models.UUIDField()),
                ("emoji", models.CharField(max_length=32)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "comment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reactions",
                        to="gateway_comments.projectcomment",
                    ),
                ),
            ],
            options={
                "db_table": "comment_reactions",
                "unique_together": {("comment", "user_id", "emoji")},
            },
        ),
        migrations.CreateModel(
            name="CommentReadStatus",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("project_id", models.UUIDField()),
                ("user_id", models.UUIDField()),
                ("last_read_at", models.DateTimeField()),
            ],
            options={
                "db_table": "comment_read_status",
                "unique_together": {("project_id", "user_id")},
            },
        ),
    ]
