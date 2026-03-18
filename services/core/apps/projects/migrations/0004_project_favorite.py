import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0003_remove_agent_mode"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProjectFavorite",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("user_id", models.UUIDField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("project", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="favorites", to="projects.project")),
            ],
            options={
                "db_table": "project_favorites",
                "unique_together": {("project", "user_id")},
                "indexes": [
                    models.Index(fields=["user_id"], name="idx_fav_user"),
                    models.Index(fields=["project"], name="idx_fav_project"),
                ],
            },
        ),
    ]
