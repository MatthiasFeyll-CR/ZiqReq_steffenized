import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ChatContextSummary",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("project_id", models.UUIDField()),
                ("summary_text", models.TextField()),
                ("messages_covered_up_to_id", models.UUIDField()),
                ("compression_iteration", models.IntegerField(default=1)),
                ("context_window_usage_at_compression", models.FloatField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "db_table": "chat_context_summaries",
            },
        ),
        migrations.CreateModel(
            name="FacilitatorContextBucket",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("content", models.TextField(default="")),
                ("updated_by", models.UUIDField(blank=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "facilitator_context_bucket",
            },
        ),
        migrations.CreateModel(
            name="ContextAgentBucket",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("sections", models.JSONField(default=dict)),
                ("free_text", models.TextField(default="")),
                ("updated_by", models.UUIDField(blank=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "context_agent_bucket",
            },
        ),
        migrations.AddIndex(
            model_name="chatcontextsummary",
            index=models.Index(fields=["project_id"], name="idx_ctx_summary_project"),
        ),
    ]
