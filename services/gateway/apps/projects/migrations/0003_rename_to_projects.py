"""Gateway mirror model rename: ideas → projects, idea_collaborators → project_collaborators.

The actual table renames are handled by core migration 0004_rename_to_projects.
This migration is a no-op on the database side — it only updates Django's migration
state so the ORM stays in sync with the renamed models and db_table values.
"""

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("gateway_projects", "0002_userreaction"),
    ]

    operations = [
        # State-only: Django needs to know the model/table names changed.
        # The actual DDL is in core's 0004_rename_to_projects migration.
        migrations.RunSQL(
            sql=migrations.RunSQL.noop,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
