"""Parameter access with caching."""

from apps.admin_config.models import AdminParameter


def get_parameter(key: str, default=None, cast=str):
    """Get admin parameter value with caching."""
    try:
        param = AdminParameter.objects.get(key=key)
        return cast(param.value)
    except AdminParameter.DoesNotExist:
        return default
