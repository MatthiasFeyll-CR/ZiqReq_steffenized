from rest_framework import serializers


class ProjectCreateSerializer(serializers.Serializer):
    project_type = serializers.ChoiceField(choices=["software", "non_software"])
    first_message = serializers.CharField(min_length=1, required=False)


class ProjectPatchSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=500, required=False)
    agent_mode = serializers.ChoiceField(
        choices=["interactive", "silent"], required=False
    )

    def validate(self, attrs):  # type: ignore[override]
        if not attrs:
            raise serializers.ValidationError("At least one field must be provided.")
        return attrs


class ProjectDetailSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    title = serializers.CharField()
    project_type = serializers.CharField()
    state = serializers.CharField()
    visibility = serializers.CharField()
    agent_mode = serializers.CharField()
    owner = serializers.SerializerMethodField()
    collaborators = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    deleted_at = serializers.DateTimeField()

    def get_collaborators(self, obj):
        from apps.authentication.models import User
        from apps.projects.models import ProjectCollaborator

        collabs = ProjectCollaborator.objects.filter(project_id=obj.id)
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

