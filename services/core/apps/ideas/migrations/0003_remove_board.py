from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("ideas", "0002_remove_merge_similarity"),
    ]

    operations = [
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS board_connections CASCADE;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS board_nodes CASCADE;",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
