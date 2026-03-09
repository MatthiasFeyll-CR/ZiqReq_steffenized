import uuid

from django.db import models


class ContextChunk(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    bucket_id = models.UUIDField()
    chunk_index = models.IntegerField()
    chunk_text = models.TextField()
    token_count = models.IntegerField()
    source_section = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "context_chunks"
        unique_together = [("bucket_id", "chunk_index")]


class IdeaEmbedding(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    idea_id = models.UUIDField(unique=True)
    source_text_hash = models.CharField(max_length=64)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "idea_embeddings"
