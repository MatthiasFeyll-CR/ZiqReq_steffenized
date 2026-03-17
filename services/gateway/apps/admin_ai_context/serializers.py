from rest_framework import serializers


class FacilitatorContextSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    context_type = serializers.CharField(read_only=True)
    content = serializers.CharField(required=True, allow_blank=True)
    updated_by = serializers.UUIDField(read_only=True, allow_null=True)
    updated_at = serializers.DateTimeField(read_only=True)


class ContextAgentBucketSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    context_type = serializers.CharField(read_only=True)
    sections = serializers.JSONField(required=False, default=dict)
    free_text = serializers.CharField(required=False, allow_blank=True, default="")
    updated_by = serializers.UUIDField(read_only=True, allow_null=True)
    updated_at = serializers.DateTimeField(read_only=True)
