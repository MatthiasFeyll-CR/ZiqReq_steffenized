import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gateway_projects", "0006_project_favorite"),
    ]

    operations = [
        migrations.CreateModel(
            name="Attachment",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("message_id", models.UUIDField(blank=True, null=True)),
                ("uploader_id", models.UUIDField()),
                ("filename", models.CharField(max_length=255)),
                ("storage_key", models.CharField(max_length=500)),
                ("content_type", models.CharField(max_length=100)),
                ("size_bytes", models.BigIntegerField()),
                ("extracted_content", models.TextField(blank=True, null=True)),
                (
                    "extraction_status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("processing", "Processing"),
                            ("completed", "Completed"),
                            ("failed", "Failed"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                (
                    "thumbnail_storage_key",
                    models.CharField(blank=True, max_length=500, null=True),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attachments",
                        to="gateway_projects.project",
                    ),
                ),
            ],
            options={
                "db_table": "attachments",
                "indexes": [
                    models.Index(
                        fields=["project"],
                        name="idx_attachments_project",
                    ),
                    models.Index(
                        fields=["message_id"],
                        name="idx_attachments_message",
                    ),
                    models.Index(
                        fields=["project", "deleted_at"],
                        name="idx_attachments_project_deleted",
                    ),
                ],
            },
        ),
    ]
