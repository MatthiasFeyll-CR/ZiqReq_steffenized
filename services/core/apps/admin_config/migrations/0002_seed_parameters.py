from django.db import migrations

SEED_PARAMETERS = [
    # Application parameters (F-11.3)
    {
        "key": "chat_message_cap",
        "value": "5",
        "default_value": "5",
        "description": "Chat messages before AI processing lockout per idea",
        "data_type": "integer",
        "category": "Application",
    },
    {
        "key": "idle_timeout",
        "value": "300",
        "default_value": "300",
        "description": "Seconds before user is marked idle",
        "data_type": "integer",
        "category": "Application",
    },
    {
        "key": "idle_disconnect",
        "value": "120",
        "default_value": "120",
        "description": "Seconds in idle before connection disconnects",
        "data_type": "integer",
        "category": "Application",
    },
    {
        "key": "max_reconnection_backoff",
        "value": "30",
        "default_value": "30",
        "description": "Maximum reconnection retry interval (seconds)",
        "data_type": "integer",
        "category": "Application",
    },
    {
        "key": "soft_delete_countdown",
        "value": "30",
        "default_value": "30",
        "description": "Days before permanent deletion from trash",
        "data_type": "integer",
        "category": "Application",
    },
    {
        "key": "debounce_timer",
        "value": "3",
        "default_value": "3",
        "description": "Seconds after last chat message before AI processes",
        "data_type": "integer",
        "category": "Application",
    },
    {
        "key": "default_app_language",
        "value": "de",
        "default_value": "de",
        "description": "Default language for new users",
        "data_type": "string",
        "category": "Application",
    },
    # Infrastructure parameters
    {
        "key": "max_retry_attempts",
        "value": "3",
        "default_value": "3",
        "description": "Max retry attempts for failed operations",
        "data_type": "integer",
        "category": "Infrastructure",
    },
    {
        "key": "dlq_alert_threshold",
        "value": "10",
        "default_value": "10",
        "description": "DLQ message count triggering alert",
        "data_type": "integer",
        "category": "Infrastructure",
    },
    {
        "key": "health_check_interval",
        "value": "60",
        "default_value": "60",
        "description": "Seconds between health checks",
        "data_type": "integer",
        "category": "Infrastructure",
    },
    # AI-specific parameters
    {
        "key": "default_ai_model",
        "value": "",
        "default_value": "",
        "description": "Azure OpenAI deployment name for default tier agents",
        "data_type": "string",
        "category": "AI",
    },
    {
        "key": "escalated_ai_model",
        "value": "",
        "default_value": "",
        "description": (
            "Azure OpenAI deployment name for escalated tier"
            " (Context Extension)"
        ),
        "data_type": "string",
        "category": "AI",
    },
    {
        "key": "ai_processing_timeout",
        "value": "60",
        "default_value": "60",
        "description": (
            "Seconds timeout for user-facing agent invocations"
        ),
        "data_type": "integer",
        "category": "AI",
    },
    {
        "key": "recent_message_count",
        "value": "20",
        "default_value": "20",
        "description": (
            "Number of recent chat messages included in"
            " Facilitator context"
        ),
        "data_type": "integer",
        "category": "AI",
    },
    {
        "key": "context_compression_threshold",
        "value": "60",
        "default_value": "60",
        "description": (
            "Context utilization percentage that triggers compression"
        ),
        "data_type": "integer",
        "category": "AI",
    },
    {
        "key": "context_rag_top_k",
        "value": "5",
        "default_value": "5",
        "description": "Number of chunks retrieved per RAG query",
        "data_type": "integer",
        "category": "AI",
    },
    {
        "key": "context_rag_min_similarity",
        "value": "0.7",
        "default_value": "0.7",
        "description": (
            "Minimum cosine similarity for RAG chunk retrieval"
        ),
        "data_type": "float",
        "category": "AI",
    },
]


def seed_parameters(apps, schema_editor):
    AdminParameter = apps.get_model("admin_config", "AdminParameter")
    for param in SEED_PARAMETERS:
        AdminParameter.objects.get_or_create(
            key=param["key"],
            defaults=param,
        )


def remove_parameters(apps, schema_editor):
    AdminParameter = apps.get_model("admin_config", "AdminParameter")
    keys = [p["key"] for p in SEED_PARAMETERS]
    AdminParameter.objects.filter(key__in=keys).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("admin_config", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_parameters, remove_parameters),
    ]
