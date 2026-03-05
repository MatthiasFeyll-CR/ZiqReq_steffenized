#!/bin/bash
# Ralph Wiggum - Long-running AI agent loop
# Usage: ./ralph.sh [--tool amp|claude] [max_iterations]

set -e

# Parse arguments
TOOL="amp"  # Default to amp for backwards compatibility
MODEL=""
MAX_ITERATIONS=10

while [[ $# -gt 0 ]]; do
  case $1 in
    --tool)
      TOOL="$2"
      shift 2
      ;;
    --tool=*)
      TOOL="${1#*=}"
      shift
      ;;
    --model)
      MODEL="$2"
      shift 2
      ;;
    --model=*)
      MODEL="${1#*=}"
      shift
      ;;
    *)
      # Assume it's max_iterations if it's a number
      if [[ "$1" =~ ^[0-9]+$ ]]; then
        MAX_ITERATIONS="$1"
      fi
      shift
      ;;
  esac
done

# Validate tool choice
if [[ "$TOOL" != "amp" && "$TOOL" != "claude" ]]; then
  echo "Error: Invalid tool '$TOOL'. Must be 'amp' or 'claude'."
  exit 1
fi
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PRD_FILE="$SCRIPT_DIR/prd.json"
PROGRESS_FILE="$SCRIPT_DIR/progress.txt"
ARCHIVE_DIR="$SCRIPT_DIR/archive"
LAST_BRANCH_FILE="$SCRIPT_DIR/.last-branch"
USAGE_FILE="${USAGE_FILE:-$PROJECT_ROOT/pipeline-token-usage.jsonl}"

# Archive previous run if branch changed
if [ -f "$PRD_FILE" ] && [ -f "$LAST_BRANCH_FILE" ]; then
  CURRENT_BRANCH=$(jq -r '.branchName // empty' "$PRD_FILE" 2>/dev/null || echo "")
  LAST_BRANCH=$(cat "$LAST_BRANCH_FILE" 2>/dev/null || echo "")
  
  if [ -n "$CURRENT_BRANCH" ] && [ -n "$LAST_BRANCH" ] && [ "$CURRENT_BRANCH" != "$LAST_BRANCH" ]; then
    # Archive the previous run
    DATE=$(date +%Y-%m-%d)
    # Strip "ralph/" prefix from branch name for folder
    FOLDER_NAME=$(echo "$LAST_BRANCH" | sed 's|^ralph/||')
    ARCHIVE_FOLDER="$ARCHIVE_DIR/$DATE-$FOLDER_NAME"
    
    echo "Archiving previous run: $LAST_BRANCH"
    mkdir -p "$ARCHIVE_FOLDER"
    [ -f "$PRD_FILE" ] && cp "$PRD_FILE" "$ARCHIVE_FOLDER/"
    [ -f "$PROGRESS_FILE" ] && cp "$PROGRESS_FILE" "$ARCHIVE_FOLDER/"
    echo "   Archived to: $ARCHIVE_FOLDER"
    
    # Reset progress file for new run
    echo "# Ralph Progress Log" > "$PROGRESS_FILE"
    echo "Started: $(date)" >> "$PROGRESS_FILE"
    echo "---" >> "$PROGRESS_FILE"
  fi
fi

# Track current branch
if [ -f "$PRD_FILE" ]; then
  CURRENT_BRANCH=$(jq -r '.branchName // empty' "$PRD_FILE" 2>/dev/null || echo "")
  if [ -n "$CURRENT_BRANCH" ]; then
    echo "$CURRENT_BRANCH" > "$LAST_BRANCH_FILE"
  fi
fi

# Initialize progress file if it doesn't exist
if [ ! -f "$PROGRESS_FILE" ]; then
  echo "# Ralph Progress Log" > "$PROGRESS_FILE"
  echo "Started: $(date)" >> "$PROGRESS_FILE"
  echo "---" >> "$PROGRESS_FILE"
fi

CLAUDE_MODEL_ARGS=()
if [ -n "$MODEL" ]; then
  CLAUDE_MODEL_ARGS=(--model "$MODEL")
fi

# Extract milestone ID from PRD for usage logging
RALPH_MILESTONE=0
if [ -f "$PRD_FILE" ]; then
  RALPH_MILESTONE=$(jq -r '.branchName // ""' "$PRD_FILE" 2>/dev/null | sed -n 's|ralph/m\([0-9]*\)-.*|\1|p')
  RALPH_MILESTONE="${RALPH_MILESTONE:-0}"
fi

log_ralph_usage() {
  local iteration="$1"
  local input_chars="$2"
  local output_chars="$3"
  local duration_s="$4"

  local input_tokens_est=$(( input_chars / 4 ))
  local output_tokens_est=$(( output_chars / 4 ))
  local timestamp
  timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

  local entry
  entry=$(jq -nc \
    --arg phase "ralph" \
    --arg model "${MODEL:-default}" \
    --argjson milestone "$RALPH_MILESTONE" \
    --argjson iteration "$iteration" \
    --argjson input_chars "$input_chars" \
    --argjson output_chars "$output_chars" \
    --argjson input_tokens_est "$input_tokens_est" \
    --argjson output_tokens_est "$output_tokens_est" \
    --argjson duration_s "$duration_s" \
    --arg timestamp "$timestamp" \
    '{
      timestamp: $timestamp,
      phase: $phase,
      model: $model,
      milestone: $milestone,
      iteration: $iteration,
      input_chars: $input_chars,
      output_chars: $output_chars,
      input_tokens_est: $input_tokens_est,
      output_tokens_est: $output_tokens_est,
      duration_s: $duration_s
    }')

  echo "$entry" >> "$USAGE_FILE"
}

echo "Starting Ralph - Tool: $TOOL${MODEL:+ - Model: $MODEL} - Max iterations: $MAX_ITERATIONS"

for i in $(seq 1 $MAX_ITERATIONS); do
  echo ""
  echo "==============================================================="
  echo "  Ralph Iteration $i of $MAX_ITERATIONS ($TOOL)"
  echo "==============================================================="

  local_start=$(date +%s)
  INPUT_CHARS=0

  # Run the selected tool with the ralph prompt
  if [[ "$TOOL" == "amp" ]]; then
    INPUT_CHARS=$(wc -c < "$SCRIPT_DIR/prompt.md")
    OUTPUT=$(cat "$SCRIPT_DIR/prompt.md" | amp --dangerously-allow-all 2>&1 | tee /dev/stderr) || true
  else
    INPUT_CHARS=$(wc -c < "$SCRIPT_DIR/CLAUDE.md")
    # Claude Code: use --dangerously-skip-permissions for autonomous operation, --print for output
    OUTPUT=$(claude --dangerously-skip-permissions --print "${CLAUDE_MODEL_ARGS[@]}" < "$SCRIPT_DIR/CLAUDE.md" 2>&1 | tee /dev/stderr) || true
  fi

  local_end=$(date +%s)
  log_ralph_usage "$i" "$INPUT_CHARS" "${#OUTPUT}" "$(( local_end - local_start ))"

  # Check for completion signal
  if echo "$OUTPUT" | grep -q "<promise>COMPLETE</promise>"; then
    echo ""
    echo "Ralph completed all tasks!"
    echo "Completed at iteration $i of $MAX_ITERATIONS"
    exit 0
  fi

  echo "Iteration $i complete. Continuing..."
  sleep 2
done

echo ""
echo "Ralph reached max iterations ($MAX_ITERATIONS) without completing all tasks."
echo "Check $PROGRESS_FILE for status."
exit 1
