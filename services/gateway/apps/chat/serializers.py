from rest_framework import serializers

VALID_REACTION_TYPES = ("thumbs_up", "thumbs_down", "heart")


class ChatMessageCreateSerializer(serializers.Serializer):
    content = serializers.CharField(min_length=1)


class ChatMessageResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    project_id = serializers.UUIDField()
    sender_type = serializers.CharField()
    sender_id = serializers.UUIDField(allow_null=True)
    ai_agent = serializers.CharField(allow_null=True)
    content = serializers.CharField()
    message_type = serializers.CharField()
    created_at = serializers.DateTimeField()


class ReactionCreateSerializer(serializers.Serializer):
    reaction_type = serializers.ChoiceField(choices=VALID_REACTION_TYPES)


class ReactionResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    message_id = serializers.UUIDField()
    user_id = serializers.UUIDField()
    reaction_type = serializers.CharField()
    created_at = serializers.DateTimeField()
