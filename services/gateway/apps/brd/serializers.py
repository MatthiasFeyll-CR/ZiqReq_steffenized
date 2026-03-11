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
    idea_id = serializers.UUIDField()
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
