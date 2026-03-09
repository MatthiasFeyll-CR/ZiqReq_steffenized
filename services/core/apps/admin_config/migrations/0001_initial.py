from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AdminParameter",
            fields=[
                ("key", models.CharField(max_length=100, primary_key=True, serialize=False)),
                ("value", models.CharField(max_length=500)),
                ("default_value", models.CharField(max_length=500)),
                ("description", models.TextField()),
                (
                    "data_type",
                    models.CharField(
                        choices=[
                            ("string", "String"),
                            ("integer", "Integer"),
                            ("float", "Float"),
                            ("boolean", "Boolean"),
                        ],
                        default="string",
                        max_length=20,
                    ),
                ),
                ("category", models.CharField(default="Application", max_length=50)),
                ("updated_by", models.UUIDField(blank=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "admin_parameters",
            },
        ),
        # CHECK constraint
        migrations.RunSQL(
            sql=[
                (
                    "ALTER TABLE admin_parameters"
                    " ADD CONSTRAINT chk_admin_data_type"
                    " CHECK (data_type IN"
                    " ('string','integer','float','boolean'));"
                ),
            ],
            reverse_sql=[
                "ALTER TABLE admin_parameters DROP CONSTRAINT IF EXISTS chk_admin_data_type;",
            ],
        ),
    ]
