from rest_framework import serializers

from .models import AdminParameter


class AdminParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminParameter
        fields = [
            "key",
            "value",
            "default_value",
            "description",
            "data_type",
            "category",
            "updated_by",
            "updated_at",
        ]
        read_only_fields = [
            "key",
            "default_value",
            "description",
            "data_type",
            "category",
            "updated_by",
            "updated_at",
        ]


PARAMETER_RANGE_CONSTRAINTS: dict[str, tuple[int | float, int | float]] = {
    "attachment_presigned_url_ttl": (60, 7200),
    "max_attachment_size_mb": (1, 500),
    "max_attachments_per_project": (1, 100),
    "orphan_attachment_ttl_hours": (1, 720),
    "soft_delete_retention_hours": (24, 8760),
    "attachment_upload_rate_limit": (1, 100),
    "soft_delete_countdown": (1, 365),
}


class AdminParameterUpdateSerializer(serializers.Serializer):
    value = serializers.CharField(required=True)

    def validate_value(self, value: str) -> str:
        """Validate value against the parameter's data_type and range constraints."""
        param: AdminParameter | None = self.context.get("parameter")
        if param is None:
            return value

        data_type = param.data_type
        if data_type == "integer":
            try:
                int_val = int(value)
            except (ValueError, TypeError):
                raise serializers.ValidationError(
                    f"Value must be a valid integer, got '{value}'."
                )
            constraints = PARAMETER_RANGE_CONSTRAINTS.get(param.key)
            if constraints:
                lo, hi = constraints
                if int_val < lo or int_val > hi:
                    raise serializers.ValidationError(
                        f"Value must be between {lo} and {hi}, got {int_val}."
                    )
        elif data_type == "float":
            try:
                float_val = float(value)
            except (ValueError, TypeError):
                raise serializers.ValidationError(
                    f"Value must be a valid float, got '{value}'."
                )
            constraints = PARAMETER_RANGE_CONSTRAINTS.get(param.key)
            if constraints:
                lo, hi = constraints
                if float_val < lo or float_val > hi:
                    raise serializers.ValidationError(
                        f"Value must be between {lo} and {hi}, got {float_val}."
                    )
        elif data_type == "boolean":
            if value.lower() not in ("true", "false"):
                raise serializers.ValidationError(
                    f"Value must be 'true' or 'false', got '{value}'."
                )
        return value
