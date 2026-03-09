import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ChatMessage",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("idea_id", models.UUIDField()),
                (
                    "sender_type",
                    models.CharField(
                        choices=[("user", "User"), ("ai", "AI")],
                        max_length=10,
                    ),
                ),
                ("sender_id", models.UUIDField(blank=True, null=True)),
                ("ai_agent", models.CharField(blank=True, max_length=30, null=True)),
                ("content", models.TextField()),
                (
                    "message_type",
                    models.CharField(
                        choices=[("regular", "Regular"), ("delegation", "Delegation")],
                        default="regular",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "db_table": "chat_messages",
            },
        ),
        migrations.CreateModel(
            name="AiReaction",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "message",
                    models.OneToOneField(
                        on_delete=models.deletion.CASCADE,
                        to="chat.chatmessage",
                    ),
                ),
                (
                    "reaction_type",
                    models.CharField(
                        choices=[("thumbs_up", "Thumbs Up"), ("thumbs_down", "Thumbs Down"), ("heart", "Heart")],
                        max_length=15,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "db_table": "ai_reactions",
            },
        ),
        migrations.CreateModel(
            name="UserReaction",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "message",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        to="chat.chatmessage",
                    ),
                ),
                ("user_id", models.UUIDField()),
                (
                    "reaction_type",
                    models.CharField(
                        choices=[("thumbs_up", "Thumbs Up"), ("thumbs_down", "Thumbs Down"), ("heart", "Heart")],
                        max_length=15,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "db_table": "user_reactions",
                "unique_together": {("message", "user_id")},
            },
        ),
        # Indexes
        migrations.AddIndex(
            model_name="chatmessage",
            index=models.Index(fields=["idea_id", "created_at"], name="idx_chat_idea_created"),
        ),
        migrations.AddIndex(
            model_name="chatmessage",
            index=models.Index(fields=["sender_id"], name="idx_chat_sender"),
        ),
        # CHECK constraints
        migrations.RunSQL(
            sql=[
                (
                    "ALTER TABLE chat_messages ADD CONSTRAINT"
                    " chk_chat_sender_type"
                    " CHECK (sender_type IN ('user','ai'));"
                ),
                (
                    "ALTER TABLE chat_messages ADD CONSTRAINT"
                    " chk_chat_message_type"
                    " CHECK (message_type IN ('regular','delegation'));"
                ),
                (
                    "ALTER TABLE ai_reactions ADD CONSTRAINT"
                    " chk_ai_reaction_type"
                    " CHECK (reaction_type IN"
                    " ('thumbs_up','thumbs_down','heart'));"
                ),
                (
                    "ALTER TABLE user_reactions ADD CONSTRAINT"
                    " chk_user_reaction_type"
                    " CHECK (reaction_type IN"
                    " ('thumbs_up','thumbs_down','heart'));"
                ),
            ],
            reverse_sql=[
                "ALTER TABLE chat_messages DROP CONSTRAINT IF EXISTS chk_chat_sender_type;",
                "ALTER TABLE chat_messages DROP CONSTRAINT IF EXISTS chk_chat_message_type;",
                "ALTER TABLE ai_reactions DROP CONSTRAINT IF EXISTS chk_ai_reaction_type;",
                "ALTER TABLE user_reactions DROP CONSTRAINT IF EXISTS chk_user_reaction_type;",
            ],
        ),
    ]
