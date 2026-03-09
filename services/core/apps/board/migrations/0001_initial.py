import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="BoardNode",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("idea_id", models.UUIDField()),
                (
                    "node_type",
                    models.CharField(
                        choices=[("box", "Box"), ("group", "Group"), ("free_text", "Free Text")],
                        max_length=15,
                    ),
                ),
                ("title", models.CharField(blank=True, max_length=500, null=True)),
                ("body", models.TextField(blank=True, null=True)),
                ("position_x", models.FloatField(default=0)),
                ("position_y", models.FloatField(default=0)),
                ("width", models.FloatField(blank=True, null=True)),
                ("height", models.FloatField(blank=True, null=True)),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="board.boardnode",
                    ),
                ),
                ("is_locked", models.BooleanField(default=False)),
                (
                    "created_by",
                    models.CharField(
                        choices=[("user", "User"), ("ai", "AI")],
                        max_length=10,
                    ),
                ),
                ("ai_modified_indicator", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "board_nodes",
            },
        ),
        migrations.CreateModel(
            name="BoardConnection",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("idea_id", models.UUIDField()),
                (
                    "source_node",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="outgoing",
                        to="board.boardnode",
                    ),
                ),
                (
                    "target_node",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="incoming",
                        to="board.boardnode",
                    ),
                ),
                ("label", models.CharField(blank=True, max_length=500, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "board_connections",
                "unique_together": {("source_node", "target_node")},
            },
        ),
        # BoardNode indexes
        migrations.AddIndex(
            model_name="boardnode",
            index=models.Index(fields=["idea_id"], name="idx_board_idea"),
        ),
        migrations.AddIndex(
            model_name="boardnode",
            index=models.Index(fields=["parent"], name="idx_board_parent"),
        ),
        # BoardConnection indexes
        migrations.AddIndex(
            model_name="boardconnection",
            index=models.Index(fields=["idea_id"], name="idx_conn_idea"),
        ),
        migrations.AddIndex(
            model_name="boardconnection",
            index=models.Index(fields=["source_node"], name="idx_conn_source"),
        ),
        migrations.AddIndex(
            model_name="boardconnection",
            index=models.Index(fields=["target_node"], name="idx_conn_target"),
        ),
        # CHECK constraints
        migrations.RunSQL(
            sql=[
                (
                    "ALTER TABLE board_nodes ADD CONSTRAINT"
                    " chk_board_node_type"
                    " CHECK (node_type IN ('box','group','free_text'));"
                ),
                (
                    "ALTER TABLE board_nodes ADD CONSTRAINT"
                    " chk_board_created_by"
                    " CHECK (created_by IN ('user','ai'));"
                ),
            ],
            reverse_sql=[
                "ALTER TABLE board_nodes DROP CONSTRAINT IF EXISTS chk_board_node_type;",
                "ALTER TABLE board_nodes DROP CONSTRAINT IF EXISTS chk_board_created_by;",
            ],
        ),
    ]
