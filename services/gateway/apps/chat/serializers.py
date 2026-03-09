from rest_framework import serializers


class ChatMessageCreateSerializer(serializers.Serializer):
    content = serializers.CharField(min_length=1)


class ChatMessageResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    idea_id = serializers.UUIDField()
    sender_type = serializers.CharField()
    sender_id = serializers.UUIDField(allow_null=True)
    ai_agent = serializers.CharField(allow_null=True)
    content = serializers.CharField()
    message_type = serializers.CharField()
    created_at = serializers.DateTimeField()
