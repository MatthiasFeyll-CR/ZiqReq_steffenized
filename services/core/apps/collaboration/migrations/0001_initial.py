import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="CollaborationInvitation",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("idea_id", models.UUIDField()),
                ("inviter_id", models.UUIDField()),
                ("invitee_id", models.UUIDField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("accepted", "Accepted"),
                            ("declined", "Declined"),
                            ("revoked", "Revoked"),
                        ],
                        default="pending",
                        max_length=15,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("responded_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "db_table": "collaboration_invitations",
            },
        ),
        migrations.AddIndex(
            model_name="collaborationinvitation",
            index=models.Index(fields=["invitee_id", "status"], name="idx_invite_invitee"),
        ),
        migrations.AddIndex(
            model_name="collaborationinvitation",
            index=models.Index(fields=["idea_id"], name="idx_invite_idea"),
        ),
        # CHECK constraint
        migrations.RunSQL(
            sql=[
                (
                    "ALTER TABLE collaboration_invitations"
                    " ADD CONSTRAINT chk_collab_status"
                    " CHECK (status IN"
                    " ('pending','accepted','declined','revoked'));"
                ),
            ],
            reverse_sql=[
                "ALTER TABLE collaboration_invitations DROP CONSTRAINT IF EXISTS chk_collab_status;",
            ],
        ),
    ]
