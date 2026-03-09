import django.db.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("similarity", "0001_initial"),
    ]

    operations = [
        # The partial unique index already exists (created via RunSQL in 0001).
        # Use SeparateDatabaseAndState to sync Django's state without re-creating it.
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddConstraint(
                    model_name="mergerequest",
                    constraint=models.UniqueConstraint(
                        condition=django.db.models.Q(("status", "pending")),
                        fields=("requesting_idea_id", "target_idea_id"),
                        name="uq_active_merge_request",
                    ),
                ),
            ],
            database_operations=[],
        ),
    ]
