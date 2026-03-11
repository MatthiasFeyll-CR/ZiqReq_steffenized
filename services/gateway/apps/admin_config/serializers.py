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


class AdminParameterUpdateSerializer(serializers.Serializer):
    value = serializers.CharField(required=True)

    def validate_value(self, value: str) -> str:
        """Validate value against the parameter's data_type."""
        param: AdminParameter | None = self.context.get("parameter")
        if param is None:
            return value

        data_type = param.data_type
        if data_type == "integer":
            try:
                int(value)
            except (ValueError, TypeError):
                raise serializers.ValidationError(
                    f"Value must be a valid integer, got '{value}'."
                )
        elif data_type == "float":
            try:
                float(value)
            except (ValueError, TypeError):
                raise serializers.ValidationError(
                    f"Value must be a valid float, got '{value}'."
                )
        elif data_type == "boolean":
            if value.lower() not in ("true", "false"):
                raise serializers.ValidationError(
                    f"Value must be 'true' or 'false', got '{value}'."
                )
        return value
