from rest_framework import serializers

VALID_NODE_TYPES = ("box", "group", "free_text")
VALID_CREATED_BY = ("user", "ai")


class BoardNodeCreateSerializer(serializers.Serializer):
    node_type = serializers.ChoiceField(choices=VALID_NODE_TYPES)
    title = serializers.CharField(max_length=500, required=False, allow_null=True, allow_blank=True)
    body = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    position_x = serializers.FloatField(default=0)
    position_y = serializers.FloatField(default=0)
    width = serializers.FloatField(required=False, allow_null=True)
    height = serializers.FloatField(required=False, allow_null=True)
    parent_id = serializers.UUIDField(required=False, allow_null=True)
    is_locked = serializers.BooleanField(default=False)
    created_by = serializers.ChoiceField(choices=VALID_CREATED_BY, default="user")

    def validate_body(self, value):
        if value and len(value) > 5000:
            raise serializers.ValidationError("Body must be at most 5000 characters.")
        return value


class BoardNodeUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=500, required=False, allow_null=True, allow_blank=True)
    body = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    position_x = serializers.FloatField(required=False)
    position_y = serializers.FloatField(required=False)
    width = serializers.FloatField(required=False, allow_null=True)
    height = serializers.FloatField(required=False, allow_null=True)
    parent_id = serializers.UUIDField(required=False, allow_null=True)
    is_locked = serializers.BooleanField(required=False)
    node_type = serializers.ChoiceField(choices=VALID_NODE_TYPES, required=False)

    def validate_body(self, value):
        if value and len(value) > 5000:
            raise serializers.ValidationError("Body must be at most 5000 characters.")
        return value


class BoardNodeResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    idea_id = serializers.UUIDField()
    node_type = serializers.CharField()
    title = serializers.CharField(allow_null=True)
    body = serializers.CharField(allow_null=True)
    position_x = serializers.FloatField()
    position_y = serializers.FloatField()
    width = serializers.FloatField(allow_null=True)
    height = serializers.FloatField(allow_null=True)
    parent_id = serializers.UUIDField(allow_null=True)
    is_locked = serializers.BooleanField()
    created_by = serializers.CharField()
    ai_modified_indicator = serializers.BooleanField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
