"""Seed attachment-related admin parameters."""

from __future__ import annotations

from django.db import migrations

ATTACHMENT_PARAMETERS = [
    ("max_attachment_size_mb", "100", "100", "Maximum file size per attachment in megabytes", "integer", "Attachments"),
    ("max_attachments_per_project", "10", "10", "Maximum active attachments per project", "integer", "Attachments"),
    ("max_attachments_per_message", "3", "3", "Maximum attachments per chat message", "integer", "Attachments"),
    ("attachment_upload_rate_limit", "10", "10", "Maximum uploads per minute per user", "integer", "Attachments"),
    ("attachment_presigned_url_ttl", "900", "900", "Presigned URL time-to-live in seconds", "integer", "Attachments"),
    ("attachment_extraction_max_chars", "16000", "16000", "Maximum characters for AI text extraction per attachment", "integer", "Attachments"),
    ("orphan_attachment_ttl_hours", "96", "96", "Hours before orphaned/deleted attachments are permanently removed", "integer", "Attachments"),
    ("allowed_attachment_types", "image/png,image/jpeg,image/webp,application/pdf", "image/png,image/jpeg,image/webp,application/pdf", "Comma-separated list of allowed MIME types for attachments", "string", "Attachments"),
    ("soft_delete_retention_hours", "720", "720", "Hours before hard-deleting soft-deleted attachments from storage", "integer", "Attachments"),
]


class Migration(migrations.Migration):
    dependencies = [
        ("admin_config", "0001_create_admin_parameters_table"),
    ]

    operations = [
        migrations.RunSQL(
            sql="\n".join(
                f"INSERT INTO admin_parameters (key, value, default_value, description, data_type, category, updated_at) "
                f"VALUES ('{k}', '{v}', '{dv}', '{desc}', '{dt}', '{cat}', now()) ON CONFLICT (key) DO NOTHING;"
                for k, v, dv, desc, dt, cat in ATTACHMENT_PARAMETERS
            ),
            reverse_sql="\n".join(
                f"DELETE FROM admin_parameters WHERE key = '{k}';"
                for k, _, _, _, _, _ in ATTACHMENT_PARAMETERS
            ),
        ),
    ]
