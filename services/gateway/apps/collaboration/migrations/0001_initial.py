import uuid

from django.db import migrations, models

STATUS_CHOICES = [
    ("pending", "Pending"),
    ("accepted", "Accepted"),
    ("declined", "Declined"),
    ("revoked", "Revoked"),
]


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="CollaborationInvitation",
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
                ("project_id", models.UUIDField()),
                ("inviter_id", models.UUIDField()),
                ("invitee_id", models.UUIDField()),
                (
                    "status",
                    models.CharField(
                        choices=STATUS_CHOICES,
                        default="pending",
                        max_length=15,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "responded_at",
                    models.DateTimeField(blank=True, null=True),
                ),
            ],
            options={
                "db_table": "collaboration_invitations",
            },
        ),
    ]
