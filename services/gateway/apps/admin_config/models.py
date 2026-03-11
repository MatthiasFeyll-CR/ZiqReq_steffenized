from django.db import models


class AdminParameter(models.Model):
    """Unmanaged mirror model — reads Core service's admin_parameters table."""

    DATA_TYPE_CHOICES = [
        ("string", "String"),
        ("integer", "Integer"),
        ("float", "Float"),
        ("boolean", "Boolean"),
    ]

    key = models.CharField(max_length=100, primary_key=True)
    value = models.CharField(max_length=500)
    default_value = models.CharField(max_length=500)
    description = models.TextField()
    data_type = models.CharField(max_length=20, choices=DATA_TYPE_CHOICES, default="string")
    category = models.CharField(max_length=50, default="Application")
    updated_by = models.UUIDField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = "admin_parameters"

    def __str__(self) -> str:
        return f"{self.key}={self.value}"
