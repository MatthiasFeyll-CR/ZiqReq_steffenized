from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("similarity", "0002_add_constraint_state"),
    ]

    operations = [
        migrations.AddField(
            model_name="mergerequest",
            field=models.BooleanField(default=False),
            name="manual_request",
        ),
    ]
