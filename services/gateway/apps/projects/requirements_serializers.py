
from rest_framework import serializers

VALID_PARENT_TYPES = {"epic", "milestone"}
VALID_CHILD_TYPES = {"user_story", "work_package"}
VALID_PRIORITIES = {"high", "medium", "low"}

SOFTWARE_PARENT_TYPE = "epic"
SOFTWARE_CHILD_TYPE = "user_story"
NON_SOFTWARE_PARENT_TYPE = "milestone"
NON_SOFTWARE_CHILD_TYPE = "work_package"


class RequirementsDraftResponseSerializer(serializers.Serializer):
    title = serializers.CharField(allow_null=True)
    short_description = serializers.CharField(allow_null=True)
    structure = serializers.JSONField()
    item_locks = serializers.JSONField()
    allow_information_gaps = serializers.BooleanField()
    readiness_evaluation = serializers.JSONField()


class RequirementsDraftPatchSerializer(serializers.Serializer):
    title = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    short_description = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate(self, attrs):  # type: ignore[override]
        if not attrs:
            raise serializers.ValidationError("At least one field must be provided.")
        return attrs


class RequirementsItemCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=500)
    description = serializers.CharField(required=False, allow_blank=True, default="")
    type = serializers.ChoiceField(choices=list(VALID_PARENT_TYPES))


class RequirementsItemPatchSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=500, required=False)
    description = serializers.CharField(required=False, allow_blank=True)


class RequirementsChildCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=500)
    description = serializers.CharField(required=False, allow_blank=True, default="")
    acceptance_criteria = serializers.ListField(
        child=serializers.CharField(), required=False, default=list
    )
    deliverables = serializers.ListField(
        child=serializers.CharField(), required=False, default=list
    )
    dependencies = serializers.ListField(
        child=serializers.CharField(), required=False, default=list
    )
    priority = serializers.ChoiceField(
        choices=["high", "medium", "low"], required=False, default="medium"
    )


class RequirementsChildPatchSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=500, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    acceptance_criteria = serializers.ListField(
        child=serializers.CharField(), required=False
    )
    deliverables = serializers.ListField(
        child=serializers.CharField(), required=False
    )
    dependencies = serializers.ListField(
        child=serializers.CharField(), required=False
    )
    priority = serializers.ChoiceField(
        choices=["high", "medium", "low"], required=False
    )

    def validate(self, attrs):  # type: ignore[override]
        if not attrs:
            raise serializers.ValidationError("At least one field must be provided.")
        return attrs


class RequirementsReorderSerializer(serializers.Serializer):
    item_ids = serializers.ListField(
        child=serializers.CharField(), min_length=1
    )


class RequirementsGenerateSerializer(serializers.Serializer):
    mode = serializers.ChoiceField(choices=["full", "selective", "item"])
    locked_item_ids = serializers.ListField(
        child=serializers.CharField(), required=False, default=list
    )


def get_parent_type(project_type: str) -> str:
    return SOFTWARE_PARENT_TYPE if project_type == "software" else NON_SOFTWARE_PARENT_TYPE


def get_child_type(project_type: str) -> str:
    return SOFTWARE_CHILD_TYPE if project_type == "software" else NON_SOFTWARE_CHILD_TYPE
