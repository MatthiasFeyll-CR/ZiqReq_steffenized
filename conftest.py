"""Root pytest config: collect_ignore_glob for cross-service isolation."""

collect_ignore_glob = [
    "services/*/apps/*/migrations/*",
    "frontend/*",
    "e2e/*",
    "node_modules/*",
]
