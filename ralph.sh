# -----------------------------
# Claude Profile Switching
# -----------------------------

AI_ENV_FILE="${AI_ENV_FILE:-.ai.env}"

# Load endpoint overrides from .ai.env if present so we do not hardcode them here.
if [ -f "$AI_ENV_FILE" ]; then
    set -a
    . "./$AI_ENV_FILE"
    set +a
fi

DEFAULT_CLAUDE_MODEL="claude-opus-4-6"

# Azure-Profil aktivieren
claude-azure() {
    local base_url="${ANTHROPIC_BASE_URL:-$DEFAULT_ANTHROPIC_BASE_URL}"

    export ANTHROPIC_BASE_URL="$base_url"
    export ANTHROPIC_FOUNDRY_BASE_URL="${ANTHROPIC_FOUNDRY_BASE_URL:-$base_url}"

    export ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}"
    export ANTHROPIC_FOUNDRY_API_KEY="$ANTHROPIC_API_KEY"

    export CLAUDE_MODEL="${CLAUDE_MODEL:-$DEFAULT_CLAUDE_MODEL}"
    export ANTHROPIC_DEFAULT_OPUS_MODEL="$CLAUDE_MODEL"
    export CLAUDE_CODE_USE_FOUNDRY=1
    echo "[Azure] Claude Code -> Azure AI Foundry"
}

claude-azure