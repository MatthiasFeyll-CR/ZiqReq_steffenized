from rest_framework import serializers


class SubmitIdeaSerializer(serializers.Serializer):
    message = serializers.CharField(required=False, allow_blank=True, default="")
    reviewer_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        default=list,
    )


class ReviewActionCommentSerializer(serializers.Serializer):
    comment = serializers.CharField(required=True, allow_blank=False)
