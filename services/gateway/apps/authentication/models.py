from django.contrib.postgres.fields import ArrayField
from django.db import models


class User(models.Model):
    """Shadow table synced from Azure AD."""

    id = models.UUIDField(primary_key=True)  # Azure AD object ID, NOT auto-generated
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    display_name = models.CharField(max_length=300)
    roles = ArrayField(models.CharField(max_length=20), default=list)
    email_notification_preferences = models.JSONField(default=dict)
    last_login_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users"
        indexes = [
            models.Index(fields=["email"], name="idx_users_email"),
            models.Index(fields=["display_name"], name="idx_users_display_name"),
        ]

    def __str__(self) -> str:
        return self.display_name
