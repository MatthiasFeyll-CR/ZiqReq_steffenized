import uuid

import pgvector.django
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("context", "0001_initial"),
    ]

    operations = [
        # Install pgvector extension
        migrations.RunSQL(
            sql="CREATE EXTENSION IF NOT EXISTS vector;",
            reverse_sql="DROP EXTENSION IF EXISTS vector;",
        ),
        migrations.CreateModel(
            name="ContextChunk",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("bucket_id", models.UUIDField()),
                ("chunk_index", models.IntegerField()),
                ("chunk_text", models.TextField()),
                ("token_count", models.IntegerField()),
                ("embedding", pgvector.django.VectorField(dimensions=1536)),
                ("source_section", models.CharField(blank=True, max_length=100, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "db_table": "context_chunks",
                "unique_together": {("bucket_id", "chunk_index")},
            },
        ),
        migrations.CreateModel(
            name="IdeaEmbedding",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("idea_id", models.UUIDField(unique=True)),
                ("embedding", pgvector.django.VectorField(dimensions=1536)),
                ("source_text_hash", models.CharField(max_length=64)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "idea_embeddings",
            },
        ),
        # HNSW indexes for vector similarity search
        migrations.AddIndex(
            model_name="contextchunk",
            index=pgvector.django.HnswIndex(
                name="idx_chunks_embedding",
                fields=["embedding"],
                opclasses=["vector_cosine_ops"],
                m=16,
                ef_construction=64,
            ),
        ),
        migrations.AddIndex(
            model_name="contextchunk",
            index=models.Index(fields=["bucket_id"], name="idx_chunks_bucket"),
        ),
        migrations.AddIndex(
            model_name="ideaembedding",
            index=pgvector.django.HnswIndex(
                name="idx_idea_embed_embedding",
                fields=["embedding"],
                opclasses=["vector_cosine_ops"],
                m=16,
                ef_construction=64,
            ),
        ),
    ]
