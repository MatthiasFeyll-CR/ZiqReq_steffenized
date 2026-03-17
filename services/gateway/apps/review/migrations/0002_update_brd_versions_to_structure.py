"""Update brd_versions table to use structure JSONB instead of flat sections.

Replaces 6 section columns with title, short_description, and structure JSONB.
"""

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("review", "0001_create_review_tables"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE brd_versions
                    ADD COLUMN IF NOT EXISTS title text,
                    ADD COLUMN IF NOT EXISTS short_description text,
                    ADD COLUMN IF NOT EXISTS structure jsonb NOT NULL DEFAULT '[]'::jsonb;

                -- Drop old section columns if they exist
                ALTER TABLE brd_versions
                    DROP COLUMN IF EXISTS section_title,
                    DROP COLUMN IF EXISTS section_short_description,
                    DROP COLUMN IF EXISTS section_current_workflow,
                    DROP COLUMN IF EXISTS section_affected_department,
                    DROP COLUMN IF EXISTS section_core_capabilities,
                    DROP COLUMN IF EXISTS section_success_criteria;
            """,
            reverse_sql="""
                ALTER TABLE brd_versions
                    ADD COLUMN IF NOT EXISTS section_title text,
                    ADD COLUMN IF NOT EXISTS section_short_description text,
                    ADD COLUMN IF NOT EXISTS section_current_workflow text,
                    ADD COLUMN IF NOT EXISTS section_affected_department text,
                    ADD COLUMN IF NOT EXISTS section_core_capabilities text,
                    ADD COLUMN IF NOT EXISTS section_success_criteria text;

                ALTER TABLE brd_versions
                    DROP COLUMN IF EXISTS title,
                    DROP COLUMN IF EXISTS short_description,
                    DROP COLUMN IF EXISTS structure;
            """,
        ),
    ]
