import os
import uuid

from django.db import migrations

DEV_USERS = [
    {
        "id": uuid.UUID("00000000-0000-0000-0000-000000000001"),
        "email": "matthias.feyll@commerzreal.com",
        "first_name": "Dev",
        "last_name": "User1",
        "display_name": "Dev User 1",
        "roles": ["user"],
    },
    {
        "id": uuid.UUID("00000000-0000-0000-0000-000000000002"),
        "email": "dev2@ziqreq.local",
        "first_name": "Dev",
        "last_name": "User2",
        "display_name": "Dev User 2",
        "roles": ["user"],
    },
    {
        "id": uuid.UUID("00000000-0000-0000-0000-000000000003"),
        "email": "dev3@ziqreq.local",
        "first_name": "Dev",
        "last_name": "User3",
        "display_name": "Dev User 3",
        "roles": ["user", "reviewer"],
    },
    {
        "id": uuid.UUID("00000000-0000-0000-0000-000000000004"),
        "email": "dev4@ziqreq.local",
        "first_name": "Dev",
        "last_name": "User4",
        "display_name": "Dev User 4",
        "roles": ["user", "admin"],
    },
]


def seed_dev_users(apps, schema_editor):
    debug = os.environ.get("DEBUG", "False").lower() == "true"
    if not debug:
        return

    User = apps.get_model("authentication", "User")
    for user_data in DEV_USERS:
        User.objects.get_or_create(
            id=user_data["id"],
            defaults=user_data,
        )


def remove_dev_users(apps, schema_editor):
    User = apps.get_model("authentication", "User")
    ids = [u["id"] for u in DEV_USERS]
    User.objects.filter(id__in=ids).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("authentication", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_dev_users, remove_dev_users),
    ]
