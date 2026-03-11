"""Monitoring dashboard serializers — US-003."""

from rest_framework import serializers


class ServiceHealthSerializer(serializers.Serializer):
    status = serializers.CharField()
    last_check = serializers.CharField(allow_null=True)


class AIProcessingSerializer(serializers.Serializer):
    request_count = serializers.IntegerField()
    success_count = serializers.IntegerField()
    failure_count = serializers.IntegerField()


class IdeasByStateSerializer(serializers.Serializer):
    open = serializers.IntegerField()
    in_review = serializers.IntegerField()
    accepted = serializers.IntegerField()
    dropped = serializers.IntegerField()
    rejected = serializers.IntegerField()


class MonitoringDashboardSerializer(serializers.Serializer):
    active_connections = serializers.IntegerField()
    ideas_by_state = IdeasByStateSerializer()
    active_users = serializers.IntegerField()
    online_users = serializers.IntegerField()
    ai_processing = AIProcessingSerializer()
    system_health = serializers.DictField(child=ServiceHealthSerializer())


class MonitoringAlertConfigSerializer(serializers.Serializer):
    user_id = serializers.UUIDField(read_only=True)
    is_active = serializers.BooleanField()


class MonitoringAlertConfigUpdateSerializer(serializers.Serializer):
    is_active = serializers.BooleanField(required=True)
