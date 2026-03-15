import django.contrib.postgres.fields
import django.db.models
import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="IdeaKeywords",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("idea_id", models.UUIDField(unique=True)),
                ("keywords", django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), default=list, size=None)),
                ("last_updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "idea_keywords",
            },
        ),
        migrations.CreateModel(
            name="MergeRequest",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("requesting_idea_id", models.UUIDField()),
                ("target_idea_id", models.UUIDField()),
                ("merge_type", models.CharField(choices=[("merge", "Merge"), ("append", "Append")], max_length=10)),
                ("requested_by", models.UUIDField()),
                ("status", models.CharField(choices=[("pending", "Pending"), ("accepted", "Accepted"), ("declined", "Declined")], default="pending", max_length=15)),
                ("requesting_owner_consent", models.CharField(choices=[("accepted", "Accepted"), ("pending", "Pending")], default="accepted", max_length=15)),
                ("target_owner_consent", models.CharField(choices=[("accepted", "Accepted"), ("pending", "Pending"), ("declined", "Declined")], default="pending", max_length=15)),
                ("reviewer_consent", models.CharField(choices=[("accepted", "Accepted"), ("pending", "Pending"), ("declined", "Declined"), ("not_required", "Not Required")], default="not_required", max_length=20)),
                ("resulting_idea_id", models.UUIDField(blank=True, null=True)),
                ("manual_request", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("resolved_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "db_table": "merge_requests",
            },
        ),
        migrations.AddIndex(
            model_name="mergerequest",
            index=models.Index(fields=["target_idea_id", "status"], name="idx_merge_target"),
        ),
        migrations.AddIndex(
            model_name="mergerequest",
            index=models.Index(fields=["requesting_idea_id", "status"], name="idx_merge_requesting"),
        ),
        migrations.AddConstraint(
            model_name="mergerequest",
            constraint=models.UniqueConstraint(
                condition=models.Q(("status", "pending")),
                fields=("requesting_idea_id", "target_idea_id"),
                name="uq_active_merge_request",
            ),
        ),
    ]
