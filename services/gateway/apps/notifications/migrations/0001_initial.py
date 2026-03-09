import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Notification",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("user_id", models.UUIDField()),
                ("event_type", models.CharField(max_length=50)),
                ("title", models.CharField(max_length=300)),
                ("body", models.TextField()),
                ("reference_id", models.UUIDField(blank=True, null=True)),
                ("reference_type", models.CharField(blank=True, max_length=30, null=True)),
                ("is_read", models.BooleanField(default=False)),
                ("action_taken", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "db_table": "notifications",
            },
        ),
        migrations.AddIndex(
            model_name="notification",
            index=models.Index(
                fields=["user_id", "is_read", "action_taken"],
                name="idx_notif_user_unread",
            ),
        ),
        migrations.AddIndex(
            model_name="notification",
            index=models.Index(
                fields=["user_id", "-created_at"],
                name="idx_notif_created",
            ),
        ),
    ]
