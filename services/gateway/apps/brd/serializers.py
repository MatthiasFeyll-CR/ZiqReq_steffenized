from rest_framework import serializers

SECTION_FIELDS = [
    "section_title",
    "section_short_description",
    "section_current_workflow",
    "section_affected_department",
    "section_core_capabilities",
    "section_success_criteria",
]

# Maps section field names to lock keys (strip 'section_' prefix)
SECTION_LOCK_KEYS = {f: f.replace("section_", "") for f in SECTION_FIELDS}


class BrdDraftResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    project_id = serializers.UUIDField()
    section_title = serializers.CharField(allow_null=True)
    section_short_description = serializers.CharField(allow_null=True)
    section_current_workflow = serializers.CharField(allow_null=True)
    section_affected_department = serializers.CharField(allow_null=True)
    section_core_capabilities = serializers.CharField(allow_null=True)
    section_success_criteria = serializers.CharField(allow_null=True)
    section_locks = serializers.JSONField()
    allow_information_gaps = serializers.BooleanField()
    readiness_evaluation = serializers.JSONField()
    last_evaluated_at = serializers.DateTimeField(allow_null=True)


class BrdDraftPatchSerializer(serializers.Serializer):
    section_title = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    section_short_description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    section_current_workflow = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    section_affected_department = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    section_core_capabilities = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    section_success_criteria = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    section_locks = serializers.JSONField(required=False)
    allow_information_gaps = serializers.BooleanField(required=False)

    def validate(self, attrs):  # type: ignore[override]
        if not attrs:
            raise serializers.ValidationError("At least one field must be provided.")
        return attrs


VALID_MODES = {"full_generation", "selective_regeneration", "section_regeneration"}
VALID_SECTION_NAMES = {
    "title",
    "short_description",
    "current_workflow",
    "affected_department",
    "core_capabilities",
    "success_criteria",
}


class BrdGenerateSerializer(serializers.Serializer):
    mode = serializers.ChoiceField(choices=list(VALID_MODES))
    section_name = serializers.CharField(required=False, allow_blank=False)

    def validate(self, attrs):  # type: ignore[override]
        mode = attrs.get("mode")
        section_name = attrs.get("section_name")

        if mode == "section_regeneration":
            if not section_name:
                raise serializers.ValidationError(
                    {"section_name": "section_name is required for section_regeneration mode."}
                )
            if section_name not in VALID_SECTION_NAMES:
                raise serializers.ValidationError(
                    {"section_name": f"Invalid section_name. Must be one of: {', '.join(sorted(VALID_SECTION_NAMES))}"}
                )
        elif section_name:
            raise serializers.ValidationError(
                {"section_name": "section_name should only be provided for section_regeneration mode."}
            )

        return attrs
