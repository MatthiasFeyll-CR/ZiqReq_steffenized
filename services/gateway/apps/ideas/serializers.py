from rest_framework import serializers


class IdeaCreateSerializer(serializers.Serializer):
    first_message = serializers.CharField(min_length=1)


class IdeaPatchSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=500, required=False)
    agent_mode = serializers.ChoiceField(
        choices=["interactive", "silent"], required=False
    )

    def validate(self, attrs):  # type: ignore[override]
        if not attrs:
            raise serializers.ValidationError("At least one field must be provided.")
        return attrs


class SimilarIdeaSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    title = serializers.CharField()
    keywords = serializers.ListField(child=serializers.CharField(), default=list)
    similarity_type = serializers.ChoiceField(choices=["declined_merge", "near_threshold"])
    similarity_score = serializers.FloatField(allow_null=True, default=None)


class MergeRequestCreateSerializer(serializers.Serializer):
    target_idea_id = serializers.UUIDField(required=False)
    target_idea_url = serializers.CharField(required=False)

    def validate(self, attrs):  # type: ignore[override]
        import re

        has_id = "target_idea_id" in attrs and attrs["target_idea_id"] is not None
        has_url = "target_idea_url" in attrs and attrs["target_idea_url"]

        if not has_id and not has_url:
            raise serializers.ValidationError("Either target_idea_id or target_idea_url is required.")

        if has_url and not has_id:
            url = attrs["target_idea_url"]
            uuid_pattern = r"/idea/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})"
            match = re.search(uuid_pattern, url, re.IGNORECASE)
            if not match:
                raise serializers.ValidationError({"target_idea_url": "INVALID_UUID"})
            import uuid as _uuid

            attrs["target_idea_id"] = _uuid.UUID(match.group(1))
            attrs["_manual_request"] = True
        elif has_url and has_id:
            attrs["_manual_request"] = True
        else:
            attrs["_manual_request"] = False

        return attrs


class MergeRequestConsentSerializer(serializers.Serializer):
    consent = serializers.ChoiceField(choices=["accept", "decline"])


class MergeRequestSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    requesting_idea_id = serializers.UUIDField()
    target_idea_id = serializers.UUIDField()
    merge_type = serializers.CharField()
    status = serializers.CharField()
    requesting_owner_consent = serializers.CharField()
    target_owner_consent = serializers.CharField()
    reviewer_consent = serializers.CharField()
    manual_request = serializers.BooleanField()
    created_at = serializers.DateTimeField()
    resolved_at = serializers.DateTimeField(allow_null=True)


class IdeaDetailSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    title = serializers.CharField()
    state = serializers.CharField()
    visibility = serializers.CharField()
    agent_mode = serializers.CharField()
    owner = serializers.SerializerMethodField()
    co_owner = serializers.SerializerMethodField()
    collaborators = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    deleted_at = serializers.DateTimeField()

    def get_collaborators(self, obj):
        from apps.authentication.models import User
        from apps.ideas.models import IdeaCollaborator

        collabs = IdeaCollaborator.objects.filter(idea_id=obj.id)
        user_ids = [c.user_id for c in collabs]
        if not user_ids:
            return []
        users = {u.id: u for u in User.objects.filter(id__in=user_ids)}
        return [
            {
                "user_id": str(c.user_id),
                "display_name": users[c.user_id].display_name if c.user_id in users else "",
            }
            for c in collabs
        ]

    def get_owner(self, obj):
        user_map = self.context.get("user_map", {})
        owner = user_map.get(obj.owner_id)
        if owner:
            return {"id": str(owner.id), "display_name": owner.display_name}
        return {"id": str(obj.owner_id), "display_name": ""}

    def get_co_owner(self, obj):
        if not obj.co_owner_id:
            return None
        user_map = self.context.get("user_map", {})
        co_owner = user_map.get(obj.co_owner_id)
        if co_owner:
            return {"id": str(co_owner.id), "display_name": co_owner.display_name}
        return {"id": str(obj.co_owner_id), "display_name": ""}
