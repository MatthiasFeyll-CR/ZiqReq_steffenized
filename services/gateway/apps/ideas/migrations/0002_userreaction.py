import uuid

from django.db import migrations, models

REACTION_TYPE_CHOICES = [
    ("thumbs_up", "Thumbs Up"),
    ("thumbs_down", "Thumbs Down"),
    ("heart", "Heart"),
]


class Migration(migrations.Migration):

    dependencies = [
        ("gateway_ideas", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserReaction",
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
                ("message_id", models.UUIDField()),
                ("user_id", models.UUIDField()),
                (
                    "reaction_type",
                    models.CharField(
                        choices=REACTION_TYPE_CHOICES,
                        max_length=15,
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True),
                ),
            ],
            options={
                "db_table": "user_reactions",
                "unique_together": {("message_id", "user_id")},
            },
        ),
    ]
