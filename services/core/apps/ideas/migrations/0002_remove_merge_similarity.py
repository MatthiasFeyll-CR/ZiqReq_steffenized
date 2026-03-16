"""Drop merge/similarity/keyword tables and columns.

Tables dropped: idea_keywords, merge_requests, idea_embeddings
Columns dropped from ideas: merged_from_idea_1_id, merged_from_idea_2_id,
    closed_by_merge_id, closed_by_append_id, co_owner_id
"""

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("ideas", "0001_initial"),
    ]

    operations = [
        # Drop tables
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS idea_keywords CASCADE;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS merge_requests CASCADE;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS idea_embeddings CASCADE;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        # Drop columns from ideas table
        migrations.RunSQL(
            sql="ALTER TABLE ideas DROP COLUMN IF EXISTS merged_from_idea_1_id;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql="ALTER TABLE ideas DROP COLUMN IF EXISTS merged_from_idea_2_id;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql="ALTER TABLE ideas DROP COLUMN IF EXISTS closed_by_merge_id;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql="ALTER TABLE ideas DROP COLUMN IF EXISTS closed_by_append_id;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        # Drop co_owner_id column and its index
        migrations.RunSQL(
            sql="DROP INDEX IF EXISTS idx_ideas_co_owner;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql="ALTER TABLE ideas DROP COLUMN IF EXISTS co_owner_id;",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
