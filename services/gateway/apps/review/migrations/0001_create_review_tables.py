"""Create review tables if not exist.

Core service owns these tables, but Gateway needs them for tests and
for environments where Core has not yet migrated.
"""

from django.db import migrations


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("gateway_projects", "0001_initial"),
        ("authentication", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE TABLE IF NOT EXISTS brd_versions (
                    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
                    project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                    version_number integer NOT NULL,
                    section_title text,
                    section_short_description text,
                    section_current_workflow text,
                    section_affected_department text,
                    section_core_capabilities text,
                    section_success_criteria text,
                    pdf_file_path varchar(500),
                    created_at timestamptz NOT NULL DEFAULT now(),
                    UNIQUE (project_id, version_number)
                );
            """,
            reverse_sql="DROP TABLE IF EXISTS brd_versions;",
        ),
        migrations.RunSQL(
            sql="""
                CREATE TABLE IF NOT EXISTS review_assignments (
                    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
                    project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                    reviewer_id uuid NOT NULL REFERENCES users(id),
                    assigned_by varchar(10) NOT NULL CHECK (assigned_by IN ('submitter', 'self')),
                    assigned_at timestamptz NOT NULL DEFAULT now(),
                    unassigned_at timestamptz
                );
                CREATE UNIQUE INDEX IF NOT EXISTS uq_active_review_assignment
                    ON review_assignments (project_id, reviewer_id)
                    WHERE unassigned_at IS NULL;
            """,
            reverse_sql="DROP TABLE IF EXISTS review_assignments;",
        ),
        migrations.RunSQL(
            sql="""
                CREATE TABLE IF NOT EXISTS review_timeline_entries (
                    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
                    project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                    entry_type varchar(20) NOT NULL CHECK (entry_type IN ('comment', 'state_change', 'resubmission')),
                    author_id uuid REFERENCES users(id),
                    content text,
                    parent_entry_id uuid REFERENCES review_timeline_entries(id),
                    old_state varchar(20),
                    new_state varchar(20),
                    old_version_id uuid,
                    new_version_id uuid,
                    created_at timestamptz NOT NULL DEFAULT now()
                );
                CREATE INDEX IF NOT EXISTS idx_timeline_project
                    ON review_timeline_entries (project_id, created_at);
                CREATE INDEX IF NOT EXISTS idx_timeline_parent
                    ON review_timeline_entries (parent_entry_id);
            """,
            reverse_sql="DROP TABLE IF EXISTS review_timeline_entries;",
        ),
    ]
