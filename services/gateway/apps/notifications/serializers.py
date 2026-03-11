from rest_framework import serializers


class NotificationSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    user_id = serializers.UUIDField()
    event_type = serializers.CharField()
    title = serializers.CharField()
    body = serializers.CharField()
    reference_id = serializers.UUIDField(allow_null=True)
    reference_type = serializers.CharField(allow_null=True)
    is_read = serializers.BooleanField()
    action_taken = serializers.BooleanField()
    created_at = serializers.DateTimeField()
