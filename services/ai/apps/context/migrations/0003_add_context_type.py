"""Add context_type to facilitator_context_bucket and context_agent_bucket.

Seeds 3 rows per bucket table: global, software, non_software.
Existing row (from 0002_seed_buckets) becomes the 'global' bucket.
"""

from django.db import migrations, models


def seed_context_types(apps, schema_editor):
    FacilitatorContextBucket = apps.get_model("context", "FacilitatorContextBucket")
    ContextAgentBucket = apps.get_model("context", "ContextAgentBucket")

    # Update existing row to global
    FacilitatorContextBucket.objects.filter(context_type="").update(context_type="global")
    existing_global = FacilitatorContextBucket.objects.filter(context_type="global").first()
    if not existing_global:
        FacilitatorContextBucket.objects.create(context_type="global", content="")

    for ct in ("software", "non_software"):
        if not FacilitatorContextBucket.objects.filter(context_type=ct).exists():
            FacilitatorContextBucket.objects.create(context_type=ct, content="")

    # Same for ContextAgentBucket
    ContextAgentBucket.objects.filter(context_type="").update(context_type="global")
    existing_global = ContextAgentBucket.objects.filter(context_type="global").first()
    if not existing_global:
        ContextAgentBucket.objects.create(context_type="global", sections={}, free_text="")

    for ct in ("software", "non_software"):
        if not ContextAgentBucket.objects.filter(context_type=ct).exists():
            ContextAgentBucket.objects.create(context_type=ct, sections={}, free_text="")


def reverse_seed(apps, schema_editor):
    FacilitatorContextBucket = apps.get_model("context", "FacilitatorContextBucket")
    ContextAgentBucket = apps.get_model("context", "ContextAgentBucket")

    FacilitatorContextBucket.objects.filter(context_type__in=["software", "non_software"]).delete()
    ContextAgentBucket.objects.filter(context_type__in=["software", "non_software"]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("context", "0002_seed_buckets"),
    ]

    operations = [
        migrations.AddField(
            model_name="facilitatorcontextbucket",
            name="context_type",
            field=models.CharField(
                choices=[("global", "Global"), ("software", "Software"), ("non_software", "Non-Software")],
                default="global",
                max_length=20,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="contextagentbucket",
            name="context_type",
            field=models.CharField(
                choices=[("global", "Global"), ("software", "Software"), ("non_software", "Non-Software")],
                default="global",
                max_length=20,
            ),
            preserve_default=False,
        ),
        migrations.RunPython(seed_context_types, reverse_seed),
        migrations.AddConstraint(
            model_name="facilitatorcontextbucket",
            constraint=models.UniqueConstraint(
                fields=["context_type"],
                name="uq_facilitator_context_type",
            ),
        ),
        migrations.AddConstraint(
            model_name="contextagentbucket",
            constraint=models.UniqueConstraint(
                fields=["context_type"],
                name="uq_context_agent_context_type",
            ),
        ),
    ]
