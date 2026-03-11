"""Create facilitator_context_bucket and context_agent_bucket tables.

These are singleton tables managed by the AI service. The gateway mirrors
them as unmanaged models, but the raw SQL migration ensures the tables
exist in the shared database for both services.
"""

from django.db import migrations


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.RunSQL(
            sql="""\
            CREATE TABLE IF NOT EXISTS facilitator_context_bucket (
                id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
                content text NOT NULL DEFAULT '',
                updated_by uuid,
                updated_at timestamptz NOT NULL DEFAULT now()
            );
            """,
            reverse_sql="DROP TABLE IF EXISTS facilitator_context_bucket;",
        ),
        migrations.RunSQL(
            sql="""\
            CREATE TABLE IF NOT EXISTS context_agent_bucket (
                id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
                sections jsonb NOT NULL DEFAULT '{}',
                free_text text NOT NULL DEFAULT '',
                updated_by uuid,
                updated_at timestamptz NOT NULL DEFAULT now()
            );
            """,
            reverse_sql="DROP TABLE IF EXISTS context_agent_bucket;",
        ),
    ]
