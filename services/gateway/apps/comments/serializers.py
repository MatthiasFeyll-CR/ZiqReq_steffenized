from rest_framework import serializers


class CommentCreateSerializer(serializers.Serializer):
    content = serializers.CharField(min_length=1)
    parent_id = serializers.UUIDField(required=False, allow_null=True)


class CommentUpdateSerializer(serializers.Serializer):
    content = serializers.CharField(min_length=1)


class ReactionSerializer(serializers.Serializer):
    emoji = serializers.CharField(min_length=1, max_length=32)
