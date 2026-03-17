from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0002_requirements_documents"),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE projects DROP CONSTRAINT IF EXISTS chk_projects_agent_mode;",
            reverse_sql=(
                "ALTER TABLE projects ADD CONSTRAINT chk_projects_agent_mode"
                " CHECK (agent_mode IN ('interactive','silent'));"
            ),
        ),
        migrations.RemoveField(
            model_name="project",
            name="agent_mode",
        ),
    ]
