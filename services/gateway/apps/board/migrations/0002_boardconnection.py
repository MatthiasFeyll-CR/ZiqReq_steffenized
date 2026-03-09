# Generated migration for BoardConnection

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("board", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="BoardConnection",
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
                ("idea_id", models.UUIDField()),
                ("label", models.CharField(blank=True, max_length=500, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "source_node",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="outgoing_connections",
                        to="board.boardnode",
                    ),
                ),
                (
                    "target_node",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="incoming_connections",
                        to="board.boardnode",
                    ),
                ),
            ],
            options={
                "db_table": "board_connections",
                "unique_together": {("source_node", "target_node")},
            },
        ),
    ]
