import uuid

from django.db import models
from pgvector.django import HnswIndex, VectorField


class ContextChunk(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bucket_id = models.UUIDField()
    chunk_index = models.IntegerField()
    chunk_text = models.TextField()
    token_count = models.IntegerField()
    embedding = VectorField(dimensions=1536)
    source_section = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "context_chunks"
        unique_together = [("bucket_id", "chunk_index")]
        indexes = [
            HnswIndex(
                name="idx_chunks_embedding",
                fields=["embedding"],
                opclasses=["vector_cosine_ops"],
                m=16,
                ef_construction=64,
            ),
            models.Index(fields=["bucket_id"], name="idx_chunks_bucket"),
        ]
