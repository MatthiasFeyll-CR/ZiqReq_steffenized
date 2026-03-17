"""Add context_type column to context_chunks for per-type RAG filtering."""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("embedding", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="contextchunk",
            name="context_type",
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddIndex(
            model_name="contextchunk",
            index=models.Index(fields=["context_type"], name="idx_chunks_context_type"),
        ),
    ]
