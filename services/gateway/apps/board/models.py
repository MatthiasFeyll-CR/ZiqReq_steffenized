import uuid

from django.db import models


class BoardNode(models.Model):
    NODE_TYPE_CHOICES = [("box", "Box"), ("group", "Group"), ("free_text", "Free Text")]
    CREATED_BY_CHOICES = [("user", "User"), ("ai", "AI")]

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

    def __str__(self) -> str:
        return f"BoardNode {self.node_type}: {self.title or self.id}"
