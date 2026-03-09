import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                ("id", models.UUIDField(primary_key=True, serialize=False)),
                ("email", models.EmailField(max_length=255, unique=True)),
                ("first_name", models.CharField(max_length=150)),
                ("last_name", models.CharField(max_length=150)),
                ("display_name", models.CharField(max_length=300)),
                (
                    "roles",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(max_length=20),
                        default=list,
                        size=None,
                    ),
                ),
                ("email_notification_preferences", models.JSONField(default=dict)),
                ("last_login_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "users",
            },
        ),
        migrations.AddIndex(
            model_name="user",
            index=models.Index(fields=["email"], name="idx_users_email"),
        ),
        migrations.AddIndex(
            model_name="user",
            index=models.Index(fields=["display_name"], name="idx_users_display_name"),
        ),
    ]
