from rest_framework import serializers

from apps.admin_config.services import get_parameter
from apps.attachments.serializers import AttachmentResponseSerializer

VALID_REACTION_TYPES = ("thumbs_up", "thumbs_down", "heart")


class ChatMessageCreateSerializer(serializers.Serializer):
    content = serializers.CharField(min_length=1)
    attachment_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        default=list,
    )

    def validate_attachment_ids(self, value):
        max_per_message = get_parameter("max_attachments_per_message", default=3, cast=int)
        if len(value) > max_per_message:
            raise serializers.ValidationError(
                f"Maximum {max_per_message} attachments per message."
            )
        return value


class ChatMessageResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    project_id = serializers.UUIDField()
    sender_type = serializers.CharField()
    sender_id = serializers.UUIDField(allow_null=True)
    ai_agent = serializers.CharField(allow_null=True)
    content = serializers.CharField()
    message_type = serializers.CharField()
    created_at = serializers.DateTimeField()
    attachments = AttachmentResponseSerializer(many=True, required=False, default=list)


class ReactionCreateSerializer(serializers.Serializer):
    reaction_type = serializers.ChoiceField(choices=VALID_REACTION_TYPES)


class ReactionResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    message_id = serializers.UUIDField()
    user_id = serializers.UUIDField()
    reaction_type = serializers.CharField()
    created_at = serializers.DateTimeField()
