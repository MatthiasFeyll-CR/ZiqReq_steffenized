"""Root pytest config: collect_ignore_glob."""

collect_ignore_glob = [
    "services/*/apps/*/migrations/*",
    "frontend/*",
    "node_modules/*",
]
