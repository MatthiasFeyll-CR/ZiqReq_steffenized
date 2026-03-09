from django.db import models


class AdminParameter(models.Model):
    """Unmanaged mirror model — reads Core service's admin_parameters table."""

    key = models.CharField(max_length=100, primary_key=True)
    value = models.CharField(max_length=500)
    default_value = models.CharField(max_length=500)
    description = models.TextField()
    data_type = models.CharField(max_length=20, default="string")
    category = models.CharField(max_length=50, default="Application")

    class Meta:
        managed = False
        db_table = "admin_parameters"
