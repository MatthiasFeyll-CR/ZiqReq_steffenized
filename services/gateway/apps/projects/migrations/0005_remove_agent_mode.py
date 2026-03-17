from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("gateway_projects", "0004_requirements_documents"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="project",
            name="agent_mode",
        ),
    ]
