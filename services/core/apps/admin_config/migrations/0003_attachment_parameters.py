"""Seed attachment-related admin parameters."""

from django.db import migrations

ATTACHMENT_PARAMETERS = [
    {
        "key": "max_attachment_size_mb",
        "value": "100",
        "default_value": "100",
        "description": "Maximum file size per attachment in megabytes",
        "data_type": "integer",
        "category": "Attachments",
    },
    {
        "key": "max_attachments_per_project",
        "value": "10",
        "default_value": "10",
        "description": "Maximum active attachments per project",
        "data_type": "integer",
        "category": "Attachments",
    },
    {
        "key": "max_attachments_per_message",
        "value": "3",
        "default_value": "3",
        "description": "Maximum attachments per chat message",
        "data_type": "integer",
        "category": "Attachments",
    },
    {
        "key": "attachment_upload_rate_limit",
        "value": "10",
        "default_value": "10",
        "description": "Maximum uploads per minute per user",
        "data_type": "integer",
        "category": "Attachments",
    },
    {
        "key": "attachment_presigned_url_ttl",
        "value": "900",
        "default_value": "900",
        "description": "Presigned URL time-to-live in seconds",
        "data_type": "integer",
        "category": "Attachments",
    },
    {
        "key": "attachment_extraction_max_chars",
        "value": "16000",
        "default_value": "16000",
        "description": "Maximum characters for AI text extraction per attachment",
        "data_type": "integer",
        "category": "Attachments",
    },
    {
        "key": "orphan_attachment_ttl_hours",
        "value": "96",
        "default_value": "96",
        "description": "Hours before orphaned/deleted attachments are permanently removed",
        "data_type": "integer",
        "category": "Attachments",
    },
    {
        "key": "allowed_attachment_types",
        "value": "image/png,image/jpeg,image/webp,application/pdf",
        "default_value": "image/png,image/jpeg,image/webp,application/pdf",
        "description": "Comma-separated list of allowed MIME types for attachments",
        "data_type": "string",
        "category": "Attachments",
    },
    {
        "key": "soft_delete_retention_hours",
        "value": "720",
        "default_value": "720",
        "description": "Hours before hard-deleting soft-deleted attachments from storage",
        "data_type": "integer",
        "category": "Attachments",
    },
]


def seed_parameters(apps, schema_editor):
    AdminParameter = apps.get_model("admin_config", "AdminParameter")
    for param in ATTACHMENT_PARAMETERS:
        AdminParameter.objects.get_or_create(
            key=param["key"],
            defaults=param,
        )


def remove_parameters(apps, schema_editor):
    AdminParameter = apps.get_model("admin_config", "AdminParameter")
    keys = [p["key"] for p in ATTACHMENT_PARAMETERS]
    AdminParameter.objects.filter(key__in=keys).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("admin_config", "0002_seed_parameters"),
    ]

    operations = [
        migrations.RunPython(seed_parameters, remove_parameters),
    ]
