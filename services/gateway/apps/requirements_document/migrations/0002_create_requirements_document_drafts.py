"""Create requirements_document_drafts table if not exists.

Core service owns this table, but Gateway needs it for tests and
for environments where Core has not yet migrated.
"""

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("requirements_document", "0001_create_brd_drafts"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE TABLE IF NOT EXISTS requirements_document_drafts (
                    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
                    project_id uuid NOT NULL UNIQUE,
                    title text,
                    short_description text,
                    structure jsonb NOT NULL DEFAULT '[]'::jsonb,
                    item_locks jsonb NOT NULL DEFAULT '{}'::jsonb,
                    allow_information_gaps boolean NOT NULL DEFAULT false,
                    readiness_evaluation jsonb NOT NULL DEFAULT '{}'::jsonb,
                    last_evaluated_at timestamptz,
                    created_at timestamptz NOT NULL DEFAULT now(),
                    updated_at timestamptz NOT NULL DEFAULT now()
                );
            """,
            reverse_sql="DROP TABLE IF EXISTS requirements_document_drafts;",
        ),
    ]
