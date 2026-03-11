"""Create admin_parameters table for test database.

The admin_parameters table is owned by Core service. The gateway mirrors
it as an unmanaged model, but the raw SQL migration ensures the table
exists in the test database.
"""

from __future__ import annotations

from django.db import migrations

SEED_PARAMETERS = [
    ("chat_message_cap", "5", "5", "Chat messages before AI processing lockout per idea", "integer", "Application"),
    ("idle_timeout", "300", "300", "Seconds before user is marked idle", "integer", "Application"),
    ("idle_disconnect", "120", "120", "Seconds in idle before connection disconnects", "integer", "Application"),
    ("max_reconnection_backoff", "30", "30", "Maximum reconnection retry interval (seconds)", "integer", "Application"),
    ("soft_delete_countdown", "30", "30", "Days before permanent deletion from trash", "integer", "Application"),
    ("debounce_timer", "3", "3", "Seconds after last chat message before AI processes", "integer", "Application"),
    ("default_app_language", "de", "de", "Default language for new users", "string", "Application"),
    ("max_keywords_per_idea", "20", "20", "Maximum abstract keywords per idea", "integer", "Application"),
    ("min_keyword_overlap", "7", "7", "Minimum keyword matches to trigger similarity", "integer", "Application"),
    ("similarity_time_limit", "180", "180", "Days to look back for keyword matching", "integer", "Application"),
    ("max_retry_attempts", "3", "3", "Max retry attempts for failed operations", "integer", "Infrastructure"),
    ("dlq_alert_threshold", "10", "10", "DLQ message count triggering alert", "integer", "Infrastructure"),
    ("health_check_interval", "60", "60", "Seconds between health checks", "integer", "Infrastructure"),
    ("default_ai_model", "", "", "Azure OpenAI deployment name for default tier agents", "string", "AI"),
    ("escalated_ai_model", "", "", "Azure OpenAI deployment name for escalated tier", "string", "AI"),
    ("ai_processing_timeout", "60", "60", "Seconds timeout for user-facing agent invocations", "integer", "AI"),
    ("recent_message_count", "20", "20", "Number of recent chat messages in Facilitator context", "integer", "AI"),
    (
        "context_compression_threshold", "60", "60",
        "Context utilization percentage that triggers compression", "integer", "AI",
    ),
    ("context_rag_top_k", "5", "5", "Number of chunks retrieved per RAG query", "integer", "AI"),
    ("context_rag_min_similarity", "0.7", "0.7", "Minimum cosine similarity for RAG chunk retrieval", "float", "AI"),
    (
        "similarity_vector_threshold", "0.75", "0.75",
        "Cosine similarity threshold for idea similarity detection", "float", "AI",
    ),
]


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.RunSQL(
            sql="""\
            CREATE TABLE IF NOT EXISTS admin_parameters (
                key varchar(100) PRIMARY KEY,
                value varchar(500) NOT NULL,
                default_value varchar(500) NOT NULL,
                description text NOT NULL DEFAULT '',
                data_type varchar(20) NOT NULL DEFAULT 'string'
                    CHECK (data_type IN ('string', 'integer', 'float', 'boolean')),
                category varchar(50) NOT NULL DEFAULT 'Application',
                updated_by uuid,
                updated_at timestamptz NOT NULL DEFAULT now()
            );
            """,
            reverse_sql="DROP TABLE IF EXISTS admin_parameters;",
        ),
        migrations.RunSQL(
            sql="\n".join(
                f"INSERT INTO admin_parameters (key, value, default_value, description, data_type, category, updated_at) "
                f"VALUES ('{k}', '{v}', '{dv}', '{desc}', '{dt}', '{cat}', now()) ON CONFLICT (key) DO NOTHING;"
                for k, v, dv, desc, dt, cat in SEED_PARAMETERS
            ),
            reverse_sql="DELETE FROM admin_parameters;",
        ),
    ]
