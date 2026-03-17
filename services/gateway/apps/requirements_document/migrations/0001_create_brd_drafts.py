"""Create brd_drafts table if not exists.

Core service owns this table, but Gateway needs it for tests and
for environments where Core has not yet migrated.
"""

from django.db import migrations


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE TABLE IF NOT EXISTS brd_drafts (
                    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
                    project_id uuid NOT NULL UNIQUE,
                    section_title text,
                    section_short_description text,
                    section_current_workflow text,
                    section_affected_department text,
                    section_core_capabilities text,
                    section_success_criteria text,
                    section_locks jsonb NOT NULL DEFAULT '{}',
                    allow_information_gaps boolean NOT NULL DEFAULT false,
                    readiness_evaluation jsonb NOT NULL DEFAULT '{}',
                    last_evaluated_at timestamptz,
                    created_at timestamptz NOT NULL DEFAULT now(),
                    updated_at timestamptz NOT NULL DEFAULT now()
                );
            """,
            reverse_sql="DROP TABLE IF EXISTS brd_drafts;",
        ),
    ]
