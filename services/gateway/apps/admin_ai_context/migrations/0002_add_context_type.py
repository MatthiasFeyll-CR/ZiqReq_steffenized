"""Add context_type to facilitator_context_bucket and context_agent_bucket.

Gateway mirrors are unmanaged — use RunSQL for schema changes.
Seeds 3 rows per bucket: global, software, non_software.
"""

from django.db import migrations


def add_context_type_and_seed(apps, schema_editor):
    """Add context_type column, unique constraint, and seed rows."""
    with schema_editor.connection.cursor() as cursor:
        # facilitator_context_bucket
        cursor.execute(
            "ALTER TABLE facilitator_context_bucket "
            "ADD COLUMN IF NOT EXISTS context_type varchar(20) DEFAULT 'global'"
        )
        cursor.execute(
            "UPDATE facilitator_context_bucket SET context_type = 'global' "
            "WHERE context_type IS NULL OR context_type = ''"
        )
        # Check if constraint exists before adding
        cursor.execute(
            "SELECT 1 FROM pg_constraint WHERE conname = 'uq_facilitator_context_type'"
        )
        if not cursor.fetchone():
            cursor.execute(
                "ALTER TABLE facilitator_context_bucket "
                "ADD CONSTRAINT uq_facilitator_context_type UNIQUE (context_type)"
            )
        cursor.execute(
            "INSERT INTO facilitator_context_bucket (context_type, content) "
            "SELECT 'software', '' WHERE NOT EXISTS "
            "(SELECT 1 FROM facilitator_context_bucket WHERE context_type = 'software')"
        )
        cursor.execute(
            "INSERT INTO facilitator_context_bucket (context_type, content) "
            "SELECT 'non_software', '' WHERE NOT EXISTS "
            "(SELECT 1 FROM facilitator_context_bucket WHERE context_type = 'non_software')"
        )

        # context_agent_bucket
        cursor.execute(
            "ALTER TABLE context_agent_bucket "
            "ADD COLUMN IF NOT EXISTS context_type varchar(20) DEFAULT 'global'"
        )
        cursor.execute(
            "UPDATE context_agent_bucket SET context_type = 'global' "
            "WHERE context_type IS NULL OR context_type = ''"
        )
        cursor.execute(
            "SELECT 1 FROM pg_constraint WHERE conname = 'uq_context_agent_context_type'"
        )
        if not cursor.fetchone():
            cursor.execute(
                "ALTER TABLE context_agent_bucket "
                "ADD CONSTRAINT uq_context_agent_context_type UNIQUE (context_type)"
            )
        cursor.execute(
            "INSERT INTO context_agent_bucket (context_type, sections, free_text) "
            "SELECT 'software', '{}', '' WHERE NOT EXISTS "
            "(SELECT 1 FROM context_agent_bucket WHERE context_type = 'software')"
        )
        cursor.execute(
            "INSERT INTO context_agent_bucket (context_type, sections, free_text) "
            "SELECT 'non_software', '{}', '' WHERE NOT EXISTS "
            "(SELECT 1 FROM context_agent_bucket WHERE context_type = 'non_software')"
        )

        # context_chunks — table may not exist if embedding app not migrated yet
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
            "WHERE table_name = 'context_chunks')"
        )
        if cursor.fetchone()[0]:
            cursor.execute(
                "ALTER TABLE context_chunks "
                "ADD COLUMN IF NOT EXISTS context_type varchar(20)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_chunks_context_type "
                "ON context_chunks(context_type)"
            )


def reverse_context_type(apps, schema_editor):
    """Remove context_type column and seeded rows."""
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            "DELETE FROM facilitator_context_bucket "
            "WHERE context_type IN ('software', 'non_software')"
        )
        cursor.execute(
            "ALTER TABLE facilitator_context_bucket "
            "DROP CONSTRAINT IF EXISTS uq_facilitator_context_type"
        )
        cursor.execute(
            "ALTER TABLE facilitator_context_bucket "
            "DROP COLUMN IF EXISTS context_type"
        )
        cursor.execute(
            "DELETE FROM context_agent_bucket "
            "WHERE context_type IN ('software', 'non_software')"
        )
        cursor.execute(
            "ALTER TABLE context_agent_bucket "
            "DROP CONSTRAINT IF EXISTS uq_context_agent_context_type"
        )
        cursor.execute(
            "ALTER TABLE context_agent_bucket "
            "DROP COLUMN IF EXISTS context_type"
        )
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
            "WHERE table_name = 'context_chunks')"
        )
        if cursor.fetchone()[0]:
            cursor.execute("DROP INDEX IF EXISTS idx_chunks_context_type")
            cursor.execute(
                "ALTER TABLE context_chunks DROP COLUMN IF EXISTS context_type"
            )


class Migration(migrations.Migration):
    dependencies = [
        ("admin_ai_context", "0001_create_ai_context_tables"),
    ]

    operations = [
        migrations.RunPython(add_context_type_and_seed, reverse_context_type),
    ]
