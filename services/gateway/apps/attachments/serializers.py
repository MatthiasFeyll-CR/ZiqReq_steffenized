from rest_framework import serializers


class AttachmentResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    filename = serializers.CharField()
    content_type = serializers.CharField()
    size_bytes = serializers.IntegerField()
    extraction_status = serializers.CharField()
    created_at = serializers.DateTimeField()
    deleted_at = serializers.DateTimeField(allow_null=True)
    message_id = serializers.UUIDField(allow_null=True)
