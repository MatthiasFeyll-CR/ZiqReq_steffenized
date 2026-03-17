from rest_framework import serializers


class RequirementsDocumentDraftResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    project_id = serializers.UUIDField()
    title = serializers.CharField(allow_null=True)
    short_description = serializers.CharField(allow_null=True)
    structure = serializers.JSONField()
    item_locks = serializers.JSONField()
    allow_information_gaps = serializers.BooleanField()
    readiness_evaluation = serializers.JSONField()
    last_evaluated_at = serializers.DateTimeField(allow_null=True)


class RequirementsDocumentDraftPatchSerializer(serializers.Serializer):
    title = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    short_description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    item_locks = serializers.JSONField(required=False)
    allow_information_gaps = serializers.BooleanField(required=False)

    def validate(self, attrs):  # type: ignore[override]
        if not attrs:
            raise serializers.ValidationError("At least one field must be provided.")
        return attrs


class RequirementsGenerateSerializer(serializers.Serializer):
    mode = serializers.ChoiceField(choices=["full_generation", "selective_regeneration"])


# Backwards-compatible aliases
SECTION_FIELDS = [
    "section_title",
    "section_short_description",
    "section_current_workflow",
    "section_affected_department",
    "section_core_capabilities",
    "section_success_criteria",
]
SECTION_LOCK_KEYS = {f: f.replace("section_", "") for f in SECTION_FIELDS}
BrdDraftResponseSerializer = RequirementsDocumentDraftResponseSerializer
BrdDraftPatchSerializer = RequirementsDocumentDraftPatchSerializer
BrdGenerateSerializer = RequirementsGenerateSerializer
