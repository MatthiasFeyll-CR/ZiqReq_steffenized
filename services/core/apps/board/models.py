import uuid

from django.db import models


class BoardNode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    idea_id = models.UUIDField()
    node_type = models.CharField(max_length=15)
    title = models.CharField(max_length=500, null=True, blank=True)
    body = models.TextField(null=True, blank=True)
    position_x = models.FloatField(default=0)
    position_y = models.FloatField(default=0)
    width = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True)
    is_locked = models.BooleanField(default=False)
    created_by = models.CharField(max_length=10)
    ai_modified_indicator = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "board_nodes"


class BoardConnection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    idea_id = models.UUIDField()
    source_node = models.ForeignKey(BoardNode, on_delete=models.CASCADE, related_name="outgoing")
    target_node = models.ForeignKey(BoardNode, on_delete=models.CASCADE, related_name="incoming")
    label = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "board_connections"
        unique_together = [("source_node", "target_node")]
