import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="BrdDraft",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("idea_id", models.UUIDField(unique=True)),
                ("section_title", models.TextField(blank=True, null=True)),
                ("section_short_description", models.TextField(blank=True, null=True)),
                ("section_current_workflow", models.TextField(blank=True, null=True)),
                ("section_affected_department", models.TextField(blank=True, null=True)),
                ("section_core_capabilities", models.TextField(blank=True, null=True)),
                ("section_success_criteria", models.TextField(blank=True, null=True)),
                ("section_locks", models.JSONField(default=dict)),
                ("allow_information_gaps", models.BooleanField(default=False)),
                ("readiness_evaluation", models.JSONField(default=dict)),
                ("last_evaluated_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "brd_drafts",
            },
        ),
        migrations.CreateModel(
            name="BrdVersion",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("idea_id", models.UUIDField()),
                ("version_number", models.IntegerField()),
                ("section_title", models.TextField(blank=True, null=True)),
                ("section_short_description", models.TextField(blank=True, null=True)),
                ("section_current_workflow", models.TextField(blank=True, null=True)),
                ("section_affected_department", models.TextField(blank=True, null=True)),
                ("section_core_capabilities", models.TextField(blank=True, null=True)),
                ("section_success_criteria", models.TextField(blank=True, null=True)),
                ("pdf_file_path", models.CharField(blank=True, max_length=500, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "db_table": "brd_versions",
                "unique_together": {("idea_id", "version_number")},
            },
        ),
        migrations.AddIndex(
            model_name="brdversion",
            index=models.Index(fields=["idea_id", "version_number"], name="idx_brd_ver_idea"),
        ),
    ]
