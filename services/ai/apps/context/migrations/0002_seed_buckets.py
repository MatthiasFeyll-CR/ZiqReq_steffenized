from django.db import migrations


def seed_buckets(apps, schema_editor):
    FacilitatorContextBucket = apps.get_model(
        "context", "FacilitatorContextBucket"
    )
    ContextAgentBucket = apps.get_model("context", "ContextAgentBucket")

    if not FacilitatorContextBucket.objects.exists():
        FacilitatorContextBucket.objects.create(content="")

    if not ContextAgentBucket.objects.exists():
        ContextAgentBucket.objects.create(sections={}, free_text="")


def remove_buckets(apps, schema_editor):
    FacilitatorContextBucket = apps.get_model(
        "context", "FacilitatorContextBucket"
    )
    ContextAgentBucket = apps.get_model("context", "ContextAgentBucket")

    FacilitatorContextBucket.objects.all().delete()
    ContextAgentBucket.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("context", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_buckets, remove_buckets),
    ]
