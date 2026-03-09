import uuid

from django.db import models


class BoardNode(models.Model):
    NODE_TYPE_CHOICES = [
        ("box", "Box"),
        ("group", "Group"),
        ("free_text", "Free Text"),
    ]
    CREATED_BY_CHOICES = [
        ("user", "User"),
        ("ai", "AI"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    idea_id = models.UUIDField()
    node_type = models.CharField(max_length=15, choices=NODE_TYPE_CHOICES)
    title = models.CharField(max_length=500, null=True, blank=True)
    body = models.TextField(null=True, blank=True)
    position_x = models.FloatField(default=0)
    position_y = models.FloatField(default=0)
    width = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True)
    is_locked = models.BooleanField(default=False)
    created_by = models.CharField(max_length=10, choices=CREATED_BY_CHOICES)
    ai_modified_indicator = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "board_nodes"
        indexes = [
            models.Index(fields=["idea_id"], name="idx_board_idea"),
            models.Index(fields=["parent"], name="idx_board_parent"),
        ]


class BoardConnection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    idea_id = models.UUIDField()
    source_node = models.ForeignKey(BoardNode, on_delete=models.CASCADE, related_name="outgoing")
    target_node = models.ForeignKey(BoardNode, on_delete=models.CASCADE, related_name="incoming")
    label = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "board_connections"
        unique_together = [("source_node", "target_node")]
        indexes = [
            models.Index(fields=["idea_id"], name="idx_conn_idea"),
            models.Index(fields=["source_node"], name="idx_conn_source"),
            models.Index(fields=["target_node"], name="idx_conn_target"),
        ]
