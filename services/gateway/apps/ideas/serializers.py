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


class IdeaDetailSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    title = serializers.CharField()
    state = serializers.CharField()
    visibility = serializers.CharField()
    agent_mode = serializers.CharField()
    owner = serializers.SerializerMethodField()
    co_owner = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    deleted_at = serializers.DateTimeField()

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
