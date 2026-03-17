"""Create requirements_document_drafts and requirements_document_versions tables.

Core service owns these tables, but Gateway needs them for tests and for
environments where Core has not yet migrated.
"""

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("gateway_projects", "0003_rename_to_projects"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE TABLE IF NOT EXISTS requirements_document_drafts (
                    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
                    project_id uuid NOT NULL UNIQUE REFERENCES projects(id) ON DELETE CASCADE,
                    title text,
                    short_description text,
                    structure jsonb NOT NULL DEFAULT '[]',
                    item_locks jsonb NOT NULL DEFAULT '{}',
                    allow_information_gaps boolean NOT NULL DEFAULT false,
                    readiness_evaluation jsonb NOT NULL DEFAULT '{}',
                    last_evaluated_at timestamptz,
                    created_at timestamptz NOT NULL DEFAULT now(),
                    updated_at timestamptz NOT NULL DEFAULT now()
                );
            """,
            reverse_sql="DROP TABLE IF EXISTS requirements_document_drafts;",
        ),
        migrations.RunSQL(
            sql="""
                CREATE TABLE IF NOT EXISTS requirements_document_versions (
                    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
                    project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                    version_number integer NOT NULL,
                    title text,
                    short_description text,
                    structure jsonb NOT NULL DEFAULT '[]',
                    pdf_file_path varchar(500),
                    created_at timestamptz NOT NULL DEFAULT now(),
                    UNIQUE(project_id, version_number)
                );

                CREATE INDEX IF NOT EXISTS idx_req_ver_project
                    ON requirements_document_versions(project_id, version_number);
            """,
            reverse_sql="DROP TABLE IF EXISTS requirements_document_versions;",
        ),
    ]
