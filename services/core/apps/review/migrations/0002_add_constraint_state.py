import django.db.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("review", "0001_initial"),
    ]

    operations = [
        # The partial unique index already exists (created via RunSQL in 0001).
        # Use SeparateDatabaseAndState to sync Django's state without re-creating it.
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddConstraint(
                    model_name="reviewassignment",
                    constraint=models.UniqueConstraint(
                        condition=django.db.models.Q(("unassigned_at__isnull", True)),
                        fields=("project_id", "reviewer_id"),
                        name="uq_active_review_assignment",
                    ),
                ),
            ],
            database_operations=[],
        ),
    ]
