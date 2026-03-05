#!/bin/bash
# Generic Pipeline Orchestrator — Config-driven, runs sequential milestone pipelines
# Usage: pipeline.sh --config <path> [--resume | --milestone N | --dry-run]
#
# Reads pipeline-config.json for all project-specific settings:
#   milestones, gate checks, paths, Ralph config
#
# Phases per milestone:
#   1. PRD Generation      (claude --print → PRD Writer skill)
#   2. Ralph Execution     (ralph.sh — story-by-story coding on branch)
#   3. QA + Bugfix         (claude --print → QA Engineer, max 3 cycles)
#   4. Merge + Verify      (merge to base → heavy tests → gate checks)
#   5. Reconciliation      (claude --print → Spec Reconciler skill)

set -euo pipefail

# ─── Source Guard (allows sourcing functions for testing) ─────────────────────
# When this script is sourced (e.g., by test harness), define functions only.
# When executed directly, run the full pipeline.
_PIPELINE_SOURCED=false
if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
  _PIPELINE_SOURCED=true
fi

# ─── Paths (derived after config load, unless pre-set by test harness) ────────
SCRIPT_DIR="${SCRIPT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
PROJECT_NAME="${PROJECT_NAME:-$(basename "$PROJECT_ROOT")}"

# ─── Base Branch (captured at startup — merge target for all milestones) ──────
BASE_BRANCH="${BASE_BRANCH:-$(cd "$PROJECT_ROOT" && git rev-parse --abbrev-ref HEAD)}"

# ─── Config Parsing ──────────────────────────────────────────────────────────

CONFIG_FILE="${CONFIG_FILE:-}"
STATE_FILE="${STATE_FILE:-$SCRIPT_DIR/pipeline-state.json}"
LOG_FILE="${LOG_FILE:-$SCRIPT_DIR/pipeline.log}"
USAGE_FILE="${USAGE_FILE:-$PROJECT_ROOT/pipeline-token-usage.jsonl}"

# Load config and populate all variables from pipeline-config.json
load_config() {
  local cfg="$CONFIG_FILE"
  [ -f "$cfg" ] || die "Config file not found: $cfg"

  # Validate JSON
  python3 -c "import json; json.load(open('$cfg'))" 2>/dev/null || die "Invalid JSON in $cfg"

  # Paths (with defaults)
  DOCS_DIR="$PROJECT_ROOT/$(jq -r '.paths.docs_dir // "docs"' "$cfg")"
  TASKS_DIR="$PROJECT_ROOT/$(jq -r '.paths.tasks_dir // "tasks"' "$cfg")"
  SCRIPTS_DIR_REL="$(jq -r '.paths.scripts_dir // "scripts/ralph"' "$cfg")"
  SKILLS_DIR="$(eval echo "$(jq -r '.paths.skills_dir // "~/.claude/skills"' "$cfg")")"
  QA_DIR="$PROJECT_ROOT/$(jq -r '.paths.qa_dir // "docs/08-qa"' "$cfg")"
  RECON_DIR="$PROJECT_ROOT/$(jq -r '.paths.reconciliation_dir // "docs/05-reconciliation"' "$cfg")"
  MILESTONES_DIR="$PROJECT_ROOT/$(jq -r '.paths.milestones_dir // "docs/05-milestones"' "$cfg")"
  ARCHIVE_DIR="$PROJECT_ROOT/$(jq -r '.paths.archive_dir // "scripts/ralph/archive"' "$cfg")"

  # Ralph config
  RALPH_TOOL="$(jq -r '.ralph.tool // "claude"' "$cfg")"
  RALPH_ITER_MULT="$(jq -r '.ralph.max_iterations_multiplier // 3' "$cfg")"
  RALPH_STUCK="$(jq -r '.ralph.stuck_threshold // 3' "$cfg")"

  # Model selection per phase (empty string = CLI default)
  MODEL_RALPH="$(jq -r '.models.ralph // ""' "$cfg")"
  MODEL_PRD="$(jq -r '.models.prd_generation // ""' "$cfg")"
  MODEL_QA="$(jq -r '.models.qa_review // ""' "$cfg")"
  MODEL_TEST_FIX="$(jq -r '.models.test_fix // ""' "$cfg")"
  MODEL_GATE_FIX="$(jq -r '.models.gate_fix // ""' "$cfg")"
  MODEL_RECONCILIATION="$(jq -r '.models.reconciliation // ""' "$cfg")"

  # QA config
  MAX_BUGFIX_CYCLES="$(jq -r '.qa.max_bugfix_cycles // 3' "$cfg")"

  # Gate config
  MAX_GATE_FIX_CYCLES="$(jq -r '.gate_checks.max_fix_cycles // 3' "$cfg")"

  # Retry config
  MAX_RETRIES="$(jq -r '.retry.max_retries // 3' "$cfg")"
  RETRY_BACKOFF="$(jq -r '.retry.backoff_seconds // 30' "$cfg")"

  # Test execution config — Tier 2 (post-merge, full rebuild)
  TEST_COMMAND="$(jq -r '.test_execution.test_command // ""' "$cfg")"
  INTEGRATION_TEST_COMMAND="$(jq -r '.test_execution.integration_test_command // ""' "$cfg")"
  TEST_TIMEOUT="$(jq -r '.test_execution.timeout_seconds // 300' "$cfg")"
  MAX_TEST_FIX_CYCLES="$(jq -r '.test_execution.max_fix_cycles // 5' "$cfg")"
  TEST_CONDITION="$(jq -r '.test_execution.condition // ""' "$cfg")"
  TEST_BUILD_COMMAND="$(jq -r '.test_execution.build_command // ""' "$cfg")"
  TEST_BUILD_TIMEOUT="$(jq -r '.test_execution.build_timeout_seconds // 300' "$cfg")"
  TEST_SETUP_COMMAND="$(jq -r '.test_execution.setup_command // ""' "$cfg")"
  TEST_TEARDOWN_COMMAND="$(jq -r '.test_execution.teardown_command // ""' "$cfg")"
  TEST_FORCE_TEARDOWN_COMMAND="$(jq -r '.test_execution.force_teardown_command // ""' "$cfg")"
  TEST_CHECK_COMMAND="$(jq -r '.test_execution.check_command // ""' "$cfg")"
  TEST_SETUP_TIMEOUT="$(jq -r '.test_execution.setup_timeout_seconds // 120' "$cfg")"

  # Test execution config — Tier 1 (Ralph per-story, bind-mounted code, no image rebuild)
  T1_COMPOSE_FILE="$(jq -r '.test_execution.tier1.compose_file // ""' "$cfg")"
  T1_TEARDOWN_COMMAND="$(jq -r '.test_execution.tier1.teardown_command // ""' "$cfg")"
  T1_SETUP_COMMAND="$(jq -r '.test_execution.tier1.setup_command // ""' "$cfg")"
  T1_SETUP_TIMEOUT="$(jq -r '.test_execution.tier1.setup_timeout_seconds // 120' "$cfg")"
  T1_BUILD_TIMEOUT="$(jq -r '.test_execution.tier1.build_timeout_seconds // 300' "$cfg")"
  T1_IMAGE_HASH_FILE="$(jq -r '.test_execution.tier1.image_hash_file // ".test-image-hashes"' "$cfg")"
  T1_ENV_COUNT="$(jq '.test_execution.tier1.environments // [] | length' "$cfg")"

  # Milestone count (derived)
  TOTAL_MILESTONES="$(jq '.milestones | length' "$cfg")"

  log "Config loaded: $(jq -r '.project.name // "unnamed"' "$cfg") — $TOTAL_MILESTONES milestones"
}

# Read milestone fields from config by milestone ID
cfg_milestone_slug() {
  jq -r ".milestones[] | select(.id == $1) | .slug" "$CONFIG_FILE"
}
cfg_milestone_name() {
  jq -r ".milestones[] | select(.id == $1) | .name // \"Milestone $1\"" "$CONFIG_FILE"
}
cfg_milestone_stories() {
  jq -r ".milestones[] | select(.id == $1) | .stories" "$CONFIG_FILE"
}

# Get ordered list of milestone IDs (array order = execution order)
cfg_milestone_ids() {
  jq -r '.milestones[].id' "$CONFIG_FILE"
}

# Get milestone index (0-based position in array) by ID
cfg_milestone_index() {
  jq -r ".milestones | to_entries[] | select(.value.id == $1) | .key" "$CONFIG_FILE"
}

# ─── Env Setup ────────────────────────────────────────────────────────────────

setup_env() {
  local cfg="$CONFIG_FILE"
  local source_file
  source_file="$(jq -r '.env_setup.source_file // empty' "$cfg")"
  local setup_fn
  setup_fn="$(jq -r '.env_setup.setup_function // empty' "$cfg")"

  if [ -n "$source_file" ]; then
    local resolved
    if [[ "$source_file" == /* ]]; then
      resolved="$source_file"
    else
      resolved="$PROJECT_ROOT/$source_file"
    fi
    if [ -f "$resolved" ]; then
      source "$resolved"
      log "Sourced env setup: $resolved"
      if [ -n "$setup_fn" ]; then
        "$setup_fn"
        log "Called setup function: $setup_fn"
      fi
    else
      log "WARNING: env_setup.source_file not found: $resolved"
    fi
  fi
}

# ─── Test Infrastructure Lifecycle ────────────────────────────────────────────
# Manages setup/teardown of services required by tests. Technology-agnostic —
# all commands are fully specified in pipeline-config.json by the configurator.

_TEST_INFRA_READY=false

_force_kill_test_infra() {
  if [ -n "$TEST_TEARDOWN_COMMAND" ] && [ "$TEST_TEARDOWN_COMMAND" != "null" ]; then
    timeout 30 bash -c "cd '$PROJECT_ROOT' && $TEST_TEARDOWN_COMMAND" &>/dev/null || true
  fi

  if [ -n "$TEST_FORCE_TEARDOWN_COMMAND" ] && [ "$TEST_FORCE_TEARDOWN_COMMAND" != "null" ]; then
    log "  [test-infra] Running force teardown..."
    if timeout 60 bash -c "cd '$PROJECT_ROOT' && $TEST_FORCE_TEARDOWN_COMMAND" &>/dev/null; then
      log "  [test-infra] Force teardown complete"
    else
      log "  [test-infra] WARNING: Force teardown returned non-zero"
    fi
  fi
}

ensure_test_infra() {
  if [ -z "$TEST_SETUP_COMMAND" ] || [ "$TEST_SETUP_COMMAND" = "null" ]; then
    return 0
  fi

  # Always start fresh — tear down any existing infrastructure first
  if [ "$_TEST_INFRA_READY" = true ]; then
    log "  [test-infra] Tearing down previous test infrastructure for clean slate..."
    _force_kill_test_infra
    _TEST_INFRA_READY=false
  else
    _check_and_kill_stale_infra
  fi

  # Build application images (no cache) so tests always run the latest code
  if [ -n "$TEST_BUILD_COMMAND" ] && [ "$TEST_BUILD_COMMAND" != "null" ]; then
    log "  [test-infra] Building application images..."
    log "  [test-infra] Running: $TEST_BUILD_COMMAND (timeout: ${TEST_BUILD_TIMEOUT}s)"

    local build_tmpfile
    build_tmpfile=$(mktemp)

    if timeout "$TEST_BUILD_TIMEOUT" bash -c "cd '$PROJECT_ROOT' && $TEST_BUILD_COMMAND" > "$build_tmpfile" 2>&1; then
      log "  [test-infra] Build complete"
      rm -f "$build_tmpfile"
    else
      local build_exit=$?
      log "  [test-infra] Build FAILED (exit code: $build_exit)"
      log "  [test-infra] Build output (last 30 lines):"
      tail -30 "$build_tmpfile" | while IFS= read -r line; do log "    $line"; done
      rm -f "$build_tmpfile"
      return 1
    fi
  fi

  # Start services
  log "  [test-infra] Starting fresh test infrastructure..."
  log "  [test-infra] Running: $TEST_SETUP_COMMAND (timeout: ${TEST_SETUP_TIMEOUT}s)"

  local tmpfile
  tmpfile=$(mktemp)

  if timeout "$TEST_SETUP_TIMEOUT" bash -c "cd '$PROJECT_ROOT' && $TEST_SETUP_COMMAND" > "$tmpfile" 2>&1; then
    log "  [test-infra] Infrastructure ready"
    _TEST_INFRA_READY=true
    rm -f "$tmpfile"
    return 0
  else
    local exit_code=$?
    log "  [test-infra] Setup FAILED (exit code: $exit_code)"
    log "  [test-infra] Output (last 30 lines):"
    tail -30 "$tmpfile" | while IFS= read -r line; do log "    $line"; done
    rm -f "$tmpfile"
    return 1
  fi
}

_check_and_kill_stale_infra() {
  if [ -z "$TEST_TEARDOWN_COMMAND" ] && [ -z "$TEST_FORCE_TEARDOWN_COMMAND" ]; then
    return 0
  fi
  if [ "$TEST_TEARDOWN_COMMAND" = "null" ] && [ "$TEST_FORCE_TEARDOWN_COMMAND" = "null" ]; then
    return 0
  fi

  local stale=false

  if [ -n "$TEST_CHECK_COMMAND" ] && [ "$TEST_CHECK_COMMAND" != "null" ]; then
    if timeout 10 bash -c "cd '$PROJECT_ROOT' && $TEST_CHECK_COMMAND" &>/dev/null; then
      stale=true
    fi
  else
    stale=true
  fi

  if [ "$stale" = true ]; then
    log "  [test-infra] Cleaning stale infrastructure from previous run..."
    _force_kill_test_infra
  fi
}

teardown_test_infra() {
  if [ -z "$TEST_TEARDOWN_COMMAND" ] || [ "$TEST_TEARDOWN_COMMAND" = "null" ]; then
    return 0
  fi

  if [ "$_TEST_INFRA_READY" = false ]; then
    return 0
  fi

  log "  [test-infra] Tearing down test infrastructure..."

  if timeout 60 bash -c "cd '$PROJECT_ROOT' && $TEST_TEARDOWN_COMMAND" &>/dev/null; then
    log "  [test-infra] Teardown complete"
    _TEST_INFRA_READY=false
    return 0
  fi

  log "  [test-infra] Graceful teardown failed — force killing..."
  _force_kill_test_infra
  _TEST_INFRA_READY=false
}

# ─── Tier 1 Test Infrastructure (Ralph per-story) ───────────────────────────
# Manages dev test containers with bind-mounted source code.
# Images are only rebuilt when dependency files change (hash-based detection).
# Dependency services (DB, broker, cache) use pre-built images — containers
# and volumes are removed between runs, but images are never rebuilt.

_T1_INFRA_READY=false

# Compute a hash of dependency files for a given environment index.
# Returns a stable hash string that changes only when deps change.
_t1_compute_dep_hash() {
  local env_idx="$1"
  local trigger_files
  trigger_files=$(jq -r ".test_execution.tier1.environments[$env_idx].rebuild_trigger_files // [] | .[]" "$CONFIG_FILE")

  if [ -z "$trigger_files" ]; then
    echo "no-trigger-files"
    return
  fi

  local hash_input=""
  while IFS= read -r f; do
    local fpath="$PROJECT_ROOT/$f"
    if [ -f "$fpath" ]; then
      hash_input+="$(md5sum "$fpath" 2>/dev/null || echo "missing:$f")"
    else
      hash_input+="missing:$f"
    fi
  done <<< "$trigger_files"

  echo "$hash_input" | md5sum | awk '{print $1}'
}

# Check if a Tier 1 environment needs its image rebuilt.
# Compares current dep hash against stored hash.
_t1_needs_rebuild() {
  local env_idx="$1"
  local env_name
  env_name=$(jq -r ".test_execution.tier1.environments[$env_idx].name" "$CONFIG_FILE")

  local current_hash
  current_hash=$(_t1_compute_dep_hash "$env_idx")

  local hash_file="$PROJECT_ROOT/$T1_IMAGE_HASH_FILE"
  local stored_hash=""
  if [ -f "$hash_file" ]; then
    stored_hash=$(jq -r ".[\"$env_name\"] // \"\"" "$hash_file" 2>/dev/null || echo "")
  fi

  if [ "$current_hash" = "$stored_hash" ]; then
    return 1  # no rebuild needed
  fi
  return 0  # rebuild needed
}

# Store the current dep hash for an environment after a successful build.
_t1_store_hash() {
  local env_idx="$1"
  local env_name
  env_name=$(jq -r ".test_execution.tier1.environments[$env_idx].name" "$CONFIG_FILE")

  local current_hash
  current_hash=$(_t1_compute_dep_hash "$env_idx")

  local hash_file="$PROJECT_ROOT/$T1_IMAGE_HASH_FILE"
  if [ -f "$hash_file" ]; then
    # Update existing hash file
    local tmp
    tmp=$(mktemp)
    jq --arg name "$env_name" --arg hash "$current_hash" '.[$name] = $hash' "$hash_file" > "$tmp"
    mv "$tmp" "$hash_file"
  else
    echo "{\"$env_name\": \"$current_hash\"}" > "$hash_file"
  fi
}

# Tear down all Tier 1 containers + volumes (dependency services + test containers).
_t1_teardown() {
  if [ -z "$T1_TEARDOWN_COMMAND" ] || [ "$T1_TEARDOWN_COMMAND" = "null" ]; then
    return 0
  fi

  log "  [tier1-infra] Tearing down containers + volumes..."
  if timeout 60 bash -c "cd '$PROJECT_ROOT' && $T1_TEARDOWN_COMMAND" &>/dev/null; then
    log "  [tier1-infra] Teardown complete"
  else
    log "  [tier1-infra] WARNING: Teardown returned non-zero"
  fi
  _T1_INFRA_READY=false
}

# Build test images for environments whose dependencies changed.
_t1_build_if_needed() {
  if [ "$T1_ENV_COUNT" -eq 0 ]; then
    return 0
  fi

  for i in $(seq 0 $((T1_ENV_COUNT - 1))); do
    local env_name
    env_name=$(jq -r ".test_execution.tier1.environments[$i].name" "$CONFIG_FILE")
    local build_cmd
    build_cmd=$(jq -r ".test_execution.tier1.environments[$i].build_command // \"\"" "$CONFIG_FILE")

    if [ -z "$build_cmd" ] || [ "$build_cmd" = "null" ]; then
      continue
    fi

    if _t1_needs_rebuild "$i"; then
      log "  [tier1-infra] Dependencies changed for '$env_name' — rebuilding image..."
      local tmpfile
      tmpfile=$(mktemp)
      if timeout "$T1_BUILD_TIMEOUT" bash -c "cd '$PROJECT_ROOT' && $build_cmd" > "$tmpfile" 2>&1; then
        log "  [tier1-infra] Image '$env_name' built successfully"
        _t1_store_hash "$i"
        rm -f "$tmpfile"
      else
        local exit_code=$?
        log "  [tier1-infra] Image build FAILED for '$env_name' (exit: $exit_code)"
        tail -30 "$tmpfile" | while IFS= read -r line; do log "    $line"; done
        rm -f "$tmpfile"
        return 1
      fi
    else
      log "  [tier1-infra] Image '$env_name' up-to-date (deps unchanged)"
    fi
  done
}

# Full Tier 1 setup: teardown → build if needed → start services.
# Called before every Tier 1 test run for a clean environment.
ensure_tier1_infra() {
  if [ -z "$T1_COMPOSE_FILE" ] || [ "$T1_COMPOSE_FILE" = "null" ]; then
    return 0
  fi

  # Always start fresh — tear down containers + volumes
  _t1_teardown

  # Build test images if dependency files changed
  if ! _t1_build_if_needed; then
    log "  [tier1-infra] SKIPPED — image build failed"
    return 1
  fi

  # Start dependency services + test containers
  if [ -n "$T1_SETUP_COMMAND" ] && [ "$T1_SETUP_COMMAND" != "null" ]; then
    log "  [tier1-infra] Starting fresh test infrastructure..."
    local tmpfile
    tmpfile=$(mktemp)
    if timeout "$T1_SETUP_TIMEOUT" bash -c "cd '$PROJECT_ROOT' && $T1_SETUP_COMMAND" > "$tmpfile" 2>&1; then
      log "  [tier1-infra] Infrastructure ready"
      _T1_INFRA_READY=true
      rm -f "$tmpfile"
      return 0
    else
      local exit_code=$?
      log "  [tier1-infra] Setup FAILED (exit: $exit_code)"
      tail -30 "$tmpfile" | while IFS= read -r line; do log "    $line"; done
      rm -f "$tmpfile"
      return 1
    fi
  fi
}

# Run Tier 1 tests for all configured environments.
# Each environment runs its test command via docker compose run --rm.
# Returns 0 only if ALL environments pass.
run_tier1_tests() {
  local label="${1:-tier1-tests}"

  if [ "$T1_ENV_COUNT" -eq 0 ]; then
    log "  [$label] No Tier 1 test environments configured — skipping"
    return 0
  fi

  if ! ensure_tier1_infra; then
    log "  [$label] SKIPPED — Tier 1 infrastructure not available"
    return 1
  fi

  local all_pass=true

  for i in $(seq 0 $((T1_ENV_COUNT - 1))); do
    local env_name
    env_name=$(jq -r ".test_execution.tier1.environments[$i].name" "$CONFIG_FILE")
    local test_cmd
    test_cmd=$(jq -r ".test_execution.tier1.environments[$i].test_command // \"\"" "$CONFIG_FILE")
    local condition
    condition=$(jq -r ".test_execution.tier1.environments[$i].condition // \"\"" "$CONFIG_FILE")
    local env_timeout
    env_timeout=$(jq -r ".test_execution.tier1.environments[$i].timeout_seconds // 300" "$CONFIG_FILE")

    if [ -z "$test_cmd" ] || [ "$test_cmd" = "null" ]; then
      continue
    fi

    # Check condition
    if [ -n "$condition" ] && [ "$condition" != "null" ]; then
      if ! (cd "$PROJECT_ROOT" && eval "$condition") &>/dev/null; then
        log "  [$label][$env_name] Condition not met — skipping"
        continue
      fi
    fi

    log "  [$label][$env_name] Running: $test_cmd (timeout: ${env_timeout}s)"

    local tmpfile
    tmpfile=$(mktemp)

    if timeout "$env_timeout" bash -c "cd '$PROJECT_ROOT' && $test_cmd" > "$tmpfile" 2>&1; then
      log "  [$label][$env_name] PASSED"
      rm -f "$tmpfile"
    else
      local exit_code=$?
      log "  [$label][$env_name] FAILED (exit: $exit_code)"
      TEST_OUTPUT=$(cat "$tmpfile")
      TEST_EXIT_CODE=$exit_code
      rm -f "$tmpfile"
      all_pass=false
    fi
  done

  # Tear down after test run (clean up for next invocation)
  _t1_teardown

  $all_pass && return 0 || return 1
}

teardown_tier1_infra() {
  _t1_teardown
}

# ─── Helpers ──────────────────────────────────────────────────────────────────

log() {
  local ts
  ts="$(date '+%Y-%m-%d %H:%M:%S')"
  echo "[$ts] $*" | tee -a "$LOG_FILE"
}

die() {
  log "FATAL: $*"
  teardown_tier1_infra
  teardown_test_infra
  exit 1
}

trap 'teardown_tier1_infra; teardown_test_infra' EXIT

commit_dirty_tree() {
  local msg="${1:-chore: pipeline artifacts}"
  cd "$PROJECT_ROOT"
  if ! git diff --quiet HEAD 2>/dev/null || [ -n "$(git ls-files --others --exclude-standard)" ]; then
    git add -A
    git commit -m "$msg" || true
    log "  Committed dirty tree: $msg"
  fi
}

save_state() {
  local milestone="$1" phase="$2" notes="${3:-}"
  python3 -c "
import json
d = {'current_milestone': $milestone, 'current_phase': '$phase', 'base_branch': '$BASE_BRANCH', 'timestamp': '$(date -Iseconds)', 'notes': '$notes'}
json.dump(d, open('$STATE_FILE', 'w'), indent=2)
"
  log "State saved: milestone=$milestone phase=$phase"
}

load_state() {
  if [ ! -f "$STATE_FILE" ]; then
    # Return first milestone ID and first phase
    local first_id
    first_id=$(jq -r '.milestones[0].id // 1' "$CONFIG_FILE")
    echo "$first_id prd_generation"
    return
  fi
  python3 -c "
import json
d = json.load(open('$STATE_FILE'))
print(d['current_milestone'], d['current_phase'])
"
}

load_state_branch() {
  if [ ! -f "$STATE_FILE" ]; then
    return
  fi
  python3 -c "
import json
d = json.load(open('$STATE_FILE'))
b = d.get('base_branch', '')
if b: print(b)
"
}

check_all_pass() {
  local prd_path="$1"
  python3 -c "
import json, sys
d = json.load(open('$prd_path'))
stories = d.get('userStories', [])
if not stories: sys.exit(1)
sys.exit(0 if all(s.get('passes', False) for s in stories) else 1)
"
}

extract_verdict() {
  local qa_report="$1"
  if [ ! -f "$qa_report" ]; then
    echo "MISSING"
    return
  fi
  if grep -iqP '(verdict|result)[:\s*]*\s*pass' "$qa_report"; then
    echo "PASS"
  elif grep -iqP '(verdict|result)[:\s*]*\s*fail' "$qa_report"; then
    echo "FAIL"
  else
    echo "UNKNOWN"
  fi
}

log_usage() {
  local phase="$1"
  local model="$2"
  local milestone="${3:-0}"
  local input_chars="$4"
  local output_chars="$5"
  local duration_s="$6"
  local attempts="$7"

  local input_tokens_est=$(( input_chars / 4 ))
  local output_tokens_est=$(( output_chars / 4 ))
  local timestamp
  timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

  local entry
  entry=$(jq -nc \
    --arg phase "$phase" \
    --arg model "${model:-default}" \
    --argjson milestone "$milestone" \
    --argjson input_chars "$input_chars" \
    --argjson output_chars "$output_chars" \
    --argjson input_tokens_est "$input_tokens_est" \
    --argjson output_tokens_est "$output_tokens_est" \
    --argjson duration_s "$duration_s" \
    --argjson attempts "$attempts" \
    --arg timestamp "$timestamp" \
    '{
      timestamp: $timestamp,
      phase: $phase,
      model: $model,
      milestone: $milestone,
      input_chars: $input_chars,
      output_chars: $output_chars,
      input_tokens_est: $input_tokens_est,
      output_tokens_est: $output_tokens_est,
      duration_s: $duration_s,
      attempts: $attempts
    }')

  echo "$entry" >> "$USAGE_FILE"
}

run_claude() {
  local prompt="$1"
  local model="${2:-}"
  local phase="${3:-unknown}"
  local milestone="${4:-0}"
  local attempt=0
  local output=""
  local model_args=()

  if [ -n "$model" ]; then
    model_args=(--model "$model")
    log "  Using model: $model"
  fi

  local start_time
  start_time=$(date +%s)

  while [ $attempt -lt $MAX_RETRIES ]; do
    attempt=$((attempt + 1))
    log "  Claude subprocess attempt $attempt/$MAX_RETRIES"
    local tmpfile
    tmpfile=$(mktemp)
    printf '%s' "$prompt" > "$tmpfile"
    output=$(claude --dangerously-skip-permissions --print "${model_args[@]}" < "$tmpfile" 2>&1) && { rm -f "$tmpfile"; break; }
    rm -f "$tmpfile"
    if [ $attempt -lt $MAX_RETRIES ]; then
      log "  Claude subprocess failed, retrying in ${RETRY_BACKOFF}s..."
      sleep "$RETRY_BACKOFF"
    fi
  done

  local end_time
  end_time=$(date +%s)
  local duration=$(( end_time - start_time ))
  local input_chars=${#prompt}
  local output_chars=${#output}

  log_usage "$phase" "$model" "$milestone" "$input_chars" "$output_chars" "$duration" "$attempt"

  if [ $attempt -eq $MAX_RETRIES ] && [ -z "$output" ]; then
    log "  ERROR: Claude subprocess failed after $MAX_RETRIES attempts"
    return 1
  fi

  echo "$output"
}

archive_milestone() {
  local m="$1"
  local slug
  slug=$(cfg_milestone_slug "$m")
  local dest="$ARCHIVE_DIR/m${m}-${slug}"
  mkdir -p "$dest"

  local prd="$TASKS_DIR/prd-m${m}.json"
  [ -f "$prd" ] && cp "$prd" "$dest/prd.json"

  local progress="$SCRIPT_DIR/progress.txt"
  [ -f "$progress" ] && cp "$progress" "$dest/progress.txt"

  log "  Archived M${m} (${slug}) → $dest"
}

# ─── Test Execution Engine ────────────────────────────────────────────────────

TEST_OUTPUT=""
TEST_EXIT_CODE=0

run_test_suite() {
  local label="${1:-tests}"
  local test_dir="${2:-$PROJECT_ROOT}"
  TEST_OUTPUT=""
  TEST_EXIT_CODE=0

  if [ -z "$TEST_COMMAND" ]; then
    log "  [$label] No test command configured — skipping"
    return 0
  fi

  if [ -n "$TEST_CONDITION" ] && [ "$TEST_CONDITION" != "null" ]; then
    if ! (cd "$test_dir" && eval "$TEST_CONDITION") &>/dev/null; then
      log "  [$label] Test condition not met — skipping"
      return 0
    fi
  fi

  if ! ensure_test_infra; then
    TEST_OUTPUT="Test infrastructure setup failed. Check setup_command in pipeline-config.json."
    TEST_EXIT_CODE=1
    log "  [$label] SKIPPED — test infrastructure not available"
    return 1
  fi

  log "  [$label] Running: $TEST_COMMAND (timeout: ${TEST_TIMEOUT}s)"

  local tmpfile
  tmpfile=$(mktemp)

  if timeout "$TEST_TIMEOUT" bash -c "cd '$test_dir' && $TEST_COMMAND" > "$tmpfile" 2>&1; then
    TEST_OUTPUT=$(cat "$tmpfile")
    TEST_EXIT_CODE=0
    rm -f "$tmpfile"
    log "  [$label] Tests PASSED"
    return 0
  else
    TEST_EXIT_CODE=$?
    TEST_OUTPUT=$(cat "$tmpfile")
    rm -f "$tmpfile"
    if [ "$TEST_EXIT_CODE" -eq 124 ]; then
      log "  [$label] Tests TIMED OUT after ${TEST_TIMEOUT}s"
    else
      log "  [$label] Tests FAILED (exit code: $TEST_EXIT_CODE)"
    fi
    return 1
  fi
}

# ─── Regression Analysis ─────────────────────────────────────────────────────
# Maps test files to milestones and classifies post-merge failures as
# CURRENT (from the just-merged milestone) or REGRESSION (from earlier ones).

# Update test-to-milestone registry in pipeline-state.json after a merge.
# Scans for test files added between pre-mN-merge tag and HEAD.
build_test_milestone_map() {
  local milestone="$1"

  # Find test files added by this milestone (between pre-merge tag and HEAD)
  local pre_tag="pre-m${milestone}-merge"
  local new_test_files
  new_test_files=$(git -C "$PROJECT_ROOT" diff --name-only --diff-filter=A "$pre_tag" HEAD 2>/dev/null \
    | grep -iE '(test_|_test\.|\.test\.|\.spec\.|tests/|__tests__/)' || true)

  if [ -z "$new_test_files" ]; then
    log "  [regression] No new test files in M${milestone}"
    return 0
  fi

  # Update the registry in pipeline-state.json
  local count
  count=$(echo "$new_test_files" | wc -l)
  log "  [regression] Registering $count test file(s) from M${milestone}"

  python3 -c "
import json, sys

state_file = '$STATE_FILE'
milestone = $milestone

try:
    state = json.load(open(state_file))
except (FileNotFoundError, json.JSONDecodeError):
    state = {}

registry = state.get('test_milestone_map', {})

for f in sys.stdin.read().strip().split('\n'):
    if f:
        registry[f] = milestone

state['test_milestone_map'] = registry
json.dump(state, open(state_file, 'w'), indent=2)
" <<< "$new_test_files"
}

# Look up which milestone owns a test file. Checks registry first, falls back to git log + tags.
_lookup_test_milestone() {
  local test_file="$1"
  local current_milestone="$2"

  # Check registry
  local from_registry
  from_registry=$(python3 -c "
import json
try:
    state = json.load(open('$STATE_FILE'))
    m = state.get('test_milestone_map', {}).get('$test_file')
    if m is not None: print(m)
except: pass
" 2>/dev/null)

  if [ -n "$from_registry" ]; then
    echo "$from_registry"
    return
  fi

  # Fallback: find which milestone tag range the file was first introduced in
  local first_commit
  first_commit=$(git -C "$PROJECT_ROOT" log --diff-filter=A --format='%H' -- "$test_file" 2>/dev/null | tail -1)

  if [ -z "$first_commit" ]; then
    echo "$current_milestone"
    return
  fi

  # Check which mN-complete tag contains this commit (earliest one)
  local tag
  for tag in $(git -C "$PROJECT_ROOT" tag -l 'm*-complete' --sort=version:refname 2>/dev/null); do
    if git -C "$PROJECT_ROOT" merge-base --is-ancestor "$first_commit" "$tag" 2>/dev/null; then
      # Extract milestone number from tag (e.g., m3-complete → 3)
      local tag_num="${tag#m}"
      tag_num="${tag_num%-complete}"
      echo "$tag_num"
      return
    fi
  done

  # No tag contains it — must be from the current milestone
  echo "$current_milestone"
}

# Parse test output for failing test file paths. Framework-agnostic: handles
# pytest, jest, mocha, vitest, go test, and other common formats.
_parse_failing_test_files() {
  local test_output="$1"

  echo "$test_output" | python3 -c "
import sys, re

lines = sys.stdin.read()
files = set()

# pytest: FAILED path/to/test_file.py::test_name
for m in re.finditer(r'FAILED\s+([^\s:]+\.py)', lines):
    files.add(m.group(1))

# pytest short summary: path/to/test_file.py::TestClass::test_method
for m in re.finditer(r'^([^\s]+\.py)::[\w]+', lines, re.MULTILINE):
    f = m.group(1)
    if 'test' in f.lower():
        files.add(f)

# pytest ERROR collecting: path/to/test_file.py
for m in re.finditer(r'ERROR\s+(?:collecting\s+)?([^\s]+test[^\s]*\.py)', lines):
    files.add(m.group(1))

# jest/vitest: FAIL path/to/test.spec.ts or FAIL path/to/test.test.js
for m in re.finditer(r'FAIL\s+([^\s]+\.(?:test|spec)\.[jt]sx?)', lines):
    files.add(m.group(1))

# jest: at Object.<anonymous> (path/to/test.test.js:line:col)
for m in re.finditer(r'\(([^\s()]+\.(?:test|spec)\.[jt]sx?):\d+:\d+\)', lines):
    files.add(m.group(1))

# go test: --- FAIL: TestName (path/test_file_test.go:line)
for m in re.finditer(r'([^\s]+_test\.go)', lines):
    files.add(m.group(1))

# Generic: any path-like string containing 'test' followed by a common extension
# that appears near FAIL/FAILED/ERROR keywords (within 3 lines)
for m in re.finditer(r'(?:FAIL|ERROR|BROKEN)[^\n]{0,200}?([a-zA-Z0-9_./-]*(?:test|spec)[a-zA-Z0-9_./-]*\.(?:py|js|ts|jsx|tsx|go|rs|rb))', lines, re.IGNORECASE):
    files.add(m.group(1))

for f in sorted(files):
    print(f)
" 2>/dev/null || true
}

# Classify test failures as CURRENT or REGRESSION relative to a milestone.
# Sets REGRESSION_FAILURES and CURRENT_FAILURES (newline-separated file lists).
classify_test_failures() {
  local current_milestone="$1"
  local test_output="$2"

  REGRESSION_FAILURES=""
  CURRENT_FAILURES=""

  local failing_files
  failing_files=$(_parse_failing_test_files "$test_output")

  if [ -z "$failing_files" ]; then
    log "  [regression] Could not parse failing test files from output"
    return 1
  fi

  local file
  while IFS= read -r file; do
    [ -z "$file" ] && continue
    local owner
    owner=$(_lookup_test_milestone "$file" "$current_milestone")

    if [ "$owner" -lt "$current_milestone" ]; then
      REGRESSION_FAILURES="${REGRESSION_FAILURES:+$REGRESSION_FAILURES
}$file (from M${owner})"
      log "  [regression] REGRESSION: $file (owned by M${owner})"
    else
      CURRENT_FAILURES="${CURRENT_FAILURES:+$CURRENT_FAILURES
}$file"
      log "  [regression] CURRENT: $file (owned by M${owner})"
    fi
  done <<< "$failing_files"

  return 0
}

# Build targeted fix prompt with regression context when regressions are detected.
_build_regression_fix_prompt() {
  local current_milestone="$1"
  local test_dir="$2"
  local test_tail="$3"
  local branch_name="$4"

  local merge_diff=""
  local pre_tag="pre-m${current_milestone}-merge"
  if git -C "$PROJECT_ROOT" rev-parse "$pre_tag" &>/dev/null; then
    merge_diff=$(git -C "$PROJECT_ROOT" diff "$pre_tag"..HEAD --stat 2>/dev/null | tail -40)
  fi

  # Gather archived PRD context for regressed milestones
  local regression_context=""
  local seen_milestones=""
  local line
  while IFS= read -r line; do
    [ -z "$line" ] && continue
    local owner_m
    owner_m=$(echo "$line" | grep -oP 'from M\K\d+' || true)
    [ -z "$owner_m" ] && continue

    # Deduplicate
    if echo "$seen_milestones" | grep -qw "$owner_m"; then
      continue
    fi
    seen_milestones="${seen_milestones} ${owner_m}"

    local owner_slug
    owner_slug=$(cfg_milestone_slug "$owner_m" 2>/dev/null || echo "unknown")
    local archived_prd="$ARCHIVE_DIR/m${owner_m}-${owner_slug}/prd.json"
    if [ -f "$archived_prd" ]; then
      local prd_summary
      prd_summary=$(python3 -c "
import json
d = json.load(open('$archived_prd'))
for s in d.get('userStories', []):
    print(f\"  - {s.get('id','?')}: {s.get('title','?')}\")
" 2>/dev/null || echo "  (could not parse PRD)")
      regression_context+="
### M${owner_m} (${owner_slug}) — stories that introduced the broken tests:
${prd_summary}
"
    fi
  done <<< "$REGRESSION_FAILURES"

  cat <<PROMPT
You are fixing test failures on branch $branch_name after merging milestone M${current_milestone}.
Working directory: $test_dir

The test command \`$TEST_COMMAND\` failed with exit code $TEST_EXIT_CODE.

## Failure Classification

**REGRESSION failures** — tests from PREVIOUS milestones that broke after this merge:
\`\`\`
$REGRESSION_FAILURES
\`\`\`

**Current milestone failures** — tests from M${current_milestone}:
\`\`\`
${CURRENT_FAILURES:-none}
\`\`\`

## What changed in this merge (files modified):
\`\`\`
$merge_diff
\`\`\`

## Context from previous milestones whose tests broke:
$regression_context

## Test output (last 100 lines):
\`\`\`
$test_tail
\`\`\`

## Instructions:
- **REGRESSIONS are the priority.** Previous milestone tests define a contract — they MUST pass.
- Fix SOURCE CODE from milestone M${current_milestone} to restore compatibility with previous tests.
- Do NOT modify test files from previous milestones. They are contracts, not suggestions.
- You MAY modify M${current_milestone}'s own test files only if they have a clear bug (wrong import, typo).
- Read the failing test files to understand what behavior they expect.
- Read the source files changed in the merge diff to find what broke the contract.
- Focus on assertion errors: expected vs received values show the exact contract mismatch.
- Only fix what is broken — do not refactor or add features.
- Commit each fix with message: fix: regression — <brief description>
PROMPT
}

# ─── Test Fix Cycle ──────────────────────────────────────────────────────────

run_test_fix_cycle() {
  local label="${1:-test-fix}"
  local test_dir="${2:-$PROJECT_ROOT}"
  local max_cycles="${3:-$MAX_TEST_FIX_CYCLES}"
  local current_milestone="${4:-0}"

  if [ -z "$TEST_COMMAND" ]; then
    return 0
  fi

  if run_test_suite "$label" "$test_dir"; then
    return 0
  fi

  local cycle=1
  while [ "$cycle" -le "$max_cycles" ]; do
    log "  [$label] Auto-fix cycle $cycle/$max_cycles — invoking Claude..."

    local branch_name
    branch_name=$(git -C "$test_dir" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
    local test_tail
    test_tail=$(echo "$TEST_OUTPUT" | tail -100)

    local prompt

    # Attempt regression analysis if we have a milestone context (> 0 means Phase 4)
    if [ "$current_milestone" -gt 0 ] && classify_test_failures "$current_milestone" "$TEST_OUTPUT" && [ -n "$REGRESSION_FAILURES" ]; then
      log "  [$label] Regression detected — building targeted fix prompt"
      prompt=$(_build_regression_fix_prompt "$current_milestone" "$test_dir" "$test_tail" "$branch_name")
    else
      # Standard fix prompt (no regression context, or milestone not provided)
      prompt="You are fixing test failures on branch $branch_name.
Working directory: $test_dir

The test command \`$TEST_COMMAND\` failed with exit code $TEST_EXIT_CODE.

Test output (last 100 lines):
\`\`\`
$test_tail
\`\`\`

Instructions:
- Read the failing test files and the source files they test
- Fix the SOURCE CODE to make tests pass — do NOT modify test files unless the test itself has a clear bug (wrong import, typo)
- Tests verify acceptance criteria from the PRD — the tests define correct behavior
- Focus on the actual assertion errors: expected vs received values indicate contract mismatches
- Only fix what is broken — do not refactor or add features
- Commit each fix with message: fix: test failure — <brief description>"
    fi

    run_claude "$prompt" "$MODEL_TEST_FIX" "test_fix" "$current_milestone" || log "  WARNING: Claude fix attempt $cycle failed"
    commit_dirty_tree "fix: test failures for $label (cycle $cycle)"

    if run_test_suite "$label (after fix $cycle)" "$test_dir"; then
      log "  [$label] Tests PASSED after fix cycle $cycle"
      return 0
    fi

    cycle=$((cycle + 1))
  done

  log "  [$label] Tests still FAILING after $max_cycles fix cycles"
  log "  Last failing output (tail 30):"
  echo "$TEST_OUTPUT" | tail -30 | while IFS= read -r line; do log "    $line"; done
  return 1
}

store_test_results() {
  local output_path="$1"
  local label="${2:-tests}"
  mkdir -p "$(dirname "$output_path")"
  {
    echo "# Test Results: $label"
    echo "Date: $(date -Iseconds)"
    echo "Command: $TEST_COMMAND"
    echo "Exit code: $TEST_EXIT_CODE"
    echo "Result: $([ "$TEST_EXIT_CODE" -eq 0 ] && echo "PASS" || echo "FAIL")"
    echo ""
    echo "## Output"
    echo '```'
    echo "$TEST_OUTPUT"
    echo '```'
  } > "$output_path"
}

# ─── Phase 1: PRD Generation ─────────────────────────────────────────────────

generate_prd() {
  local m="$1"
  local slug
  slug=$(cfg_milestone_slug "$m")
  local prd_json="$TASKS_DIR/prd-m${m}.json"

  log "Phase 1 (PRD): Generating PRD for M${m} (${slug})"

  # Skip if PRD already exists (resume case)
  if [ -f "$prd_json" ]; then
    log "  PRD for M${m} already exists, skipping"
    return 0
  fi

  local skill_content
  skill_content=$(cat "$SKILLS_DIR/prd_writer/SKILL.md")
  local milestone_doc="$MILESTONES_DIR/milestone-${m}.md"

  local prompt
  prompt="$skill_content

ARGUMENTS: Write PRD for milestone M${m} (${slug}).

Instructions:
- Read $milestone_doc and ALL upstream docs (architecture, design, AI, integration docs).
- Read the ACTUAL codebase for ground truth — check what previous milestones actually built.
- Read $ARCHIVE_DIR/ for learnings from previous milestone runs.
- Write the PRD markdown to $TASKS_DIR/prd-m${m}-${slug}.md
- Write the machine-readable PRD JSON to $TASKS_DIR/prd-m${m}.json
- Write the context bundle to $SCRIPT_DIR/context.md (see Section 8 of your skill instructions)
- Branch name must be: ralph/m${m}-${slug}
- Follow the exact JSON structure with userStories array, each having: id, title, description, acceptanceCriteria, priority, passes (false), notes."

  if [ "$DRY_RUN" = true ]; then
    log "  [DRY RUN] Would generate PRD for M${m}"
    return 0
  fi

  local output
  output=$(run_claude "$prompt" "$MODEL_PRD" "prd_generation" "$m") || {
    log "  ERROR: PRD generation failed for M${m}, retrying once..."
    output=$(run_claude "$prompt" "$MODEL_PRD" "prd_generation" "$m") || die "PRD generation failed for M${m} after retry"
  }

  if [ ! -f "$prd_json" ]; then
    die "PRD generation for M${m} did not produce $prd_json"
  fi

  local context_bundle="$SCRIPT_DIR/context.md"
  if [ ! -f "$context_bundle" ]; then
    log "  WARNING: PRD Writer did not produce context bundle at $context_bundle"
    log "  Ralph will fall back to reading upstream docs directly."
  fi

  log "  PRD for M${m} generated successfully"
}

# ─── Phase 2: Ralph Execution ────────────────────────────────────────────────

run_ralph() {
  local m="$1"
  local slug
  slug=$(cfg_milestone_slug "$m")
  local stories
  stories=$(cfg_milestone_stories "$m")
  local max_iter=$((stories * RALPH_ITER_MULT))
  local branch="ralph/m${m}-${slug}"
  local prd_src="$TASKS_DIR/prd-m${m}.json"

  log "Phase 2 (Ralph): M${m} (${slug}), branch=$branch, max_iter=$max_iter"

  if [ "$DRY_RUN" = true ]; then
    log "  [DRY RUN] Would run Ralph for M${m}"
    return 0
  fi

  # Set up Ralph workspace
  ln -sf "../../tasks/prd-m${m}.json" "$SCRIPT_DIR/prd.json"

  echo "# Ralph Progress Log" > "$SCRIPT_DIR/progress.txt"
  echo "Started: M${m} ${slug} — $(date)" >> "$SCRIPT_DIR/progress.txt"
  echo "---" >> "$SCRIPT_DIR/progress.txt"

  cd "$PROJECT_ROOT"
  commit_dirty_tree "chore: pipeline artifacts before M${m}"

  # Create or checkout milestone branch from current HEAD
  if git rev-parse --verify "$branch" >/dev/null 2>&1; then
    git checkout "$branch"
  else
    git checkout -b "$branch"
  fi

  # Run Ralph
  local ralph_model_args=()
  [ -n "$MODEL_RALPH" ] && ralph_model_args=(--model "$MODEL_RALPH")
  bash "$SCRIPT_DIR/ralph.sh" --tool "$RALPH_TOOL" "${ralph_model_args[@]}" "$max_iter" || true

  if check_all_pass "$prd_src"; then
    log "  Ralph: M${m} ALL PASS"
  else
    log "  Ralph: M${m} completed with some stories still failing"
  fi

  # Light test run after Ralph — log results for QA but don't block
  # Use Tier 1 (containerized) for quick feedback, fall back to Tier 2 if Tier 1 not configured
  if [ "$T1_ENV_COUNT" -gt 0 ]; then
    run_tier1_tests "post-ralph M${m}" || true
  else
    run_test_suite "post-ralph M${m}" "$PROJECT_ROOT" || true
  fi
  store_test_results "$QA_DIR/test-results-post-ralph-m${m}.md" "Post-Ralph M${m}"
}

# ─── Phase 2b: Ralph Bugfix ──────────────────────────────────────────────────

run_ralph_bugfix() {
  local m="$1"
  local slug
  slug=$(cfg_milestone_slug "$m")
  local stories
  stories=$(cfg_milestone_stories "$m")
  local max_iter=$((stories * 2))
  local branch="ralph/m${m}-${slug}"

  log "  Ralph bugfix: M${m} (${slug}), max_iter=$max_iter"

  cd "$PROJECT_ROOT"
  git checkout "$branch"
  ln -sf "../../tasks/prd-m${m}.json" "$SCRIPT_DIR/prd.json"
  local ralph_model_args=()
  [ -n "$MODEL_RALPH" ] && ralph_model_args=(--model "$MODEL_RALPH")
  bash "$SCRIPT_DIR/ralph.sh" --tool "$RALPH_TOOL" "${ralph_model_args[@]}" "$max_iter" || true
}

# ─── Test Matrix Coverage Analysis ────────────────────────────────────────────
# Pre-QA step: cross-references test matrix IDs assigned to this milestone's
# stories against actual test files in the codebase. Produces a structured
# coverage report (FOUND/MISSING per test ID) that feeds into the QA prompt.

# Extract test IDs assigned to a milestone's stories from the PRD.
# Looks for Testing: references in story notes (e.g., "Testing: T-1.2.01, T-1.2.02").
_extract_milestone_test_ids() {
  local prd_path="$1"

  python3 -c "
import json, re, sys

try:
    prd = json.load(open('$prd_path'))
except (FileNotFoundError, json.JSONDecodeError):
    sys.exit(0)

ids = set()
for story in prd.get('userStories', []):
    notes = story.get('notes', '')
    # Match test IDs like T-1.2.01, T-X.Y.ZZ, API-1.01, DB-2.03, UI-3.01, etc.
    for m in re.finditer(r'\b(T-[\d.]+|API-[\d.]+|DB-[\d.]+|UI-[\d.]+|LOOP-[\d]+|STATE-[\d]+|TIMEOUT-[\d]+|LEAK-[\d]+|INTEGRITY-[\d]+|AI-SAFE-[\d]+|SCN-[\d]+|JOURNEY-[\d]+|CONC-[\d]+|ERR-[\d]+)\b', notes):
        ids.add(m.group(1))

for tid in sorted(ids):
    print(tid)
" 2>/dev/null || true
}

# Search codebase for test ID references. Returns found IDs (one per line).
_find_implemented_test_ids() {
  local test_ids="$1"
  local search_dir="$2"

  local found_ids=""
  local tid
  while IFS= read -r tid; do
    [ -z "$tid" ] && continue
    # Normalize ID for grep: T-1.2.01 matches T-1.2.01, T_1_2_01, T_1.2.01
    local pattern
    pattern=$(echo "$tid" | sed 's/[.-]/_*/g')
    # Search test files for either the exact ID or the normalized form
    if grep -rlE "(${tid}|${pattern})" "$search_dir" \
         --include='*.py' --include='*.js' --include='*.ts' --include='*.tsx' \
         --include='*.jsx' --include='*.go' --include='*.rs' --include='*.rb' \
         2>/dev/null | head -1 | grep -q .; then
      found_ids="${found_ids:+$found_ids
}$tid"
    fi
  done <<< "$test_ids"

  echo "$found_ids"
}

# Analyze test matrix coverage for a milestone. Produces TEST_COVERAGE_REPORT.
# Returns 0 if analysis succeeded (even if tests are missing), 1 if no test matrix exists.
TEST_COVERAGE_REPORT=""

analyze_test_matrix_coverage() {
  local m="$1"
  local prd_path="$2"
  TEST_COVERAGE_REPORT=""

  local test_matrix="$DOCS_DIR/04-test-architecture/test-matrix.md"
  if [ ! -f "$test_matrix" ]; then
    log "  [coverage] No test matrix found — skipping coverage analysis"
    return 1
  fi

  if [ ! -f "$prd_path" ]; then
    log "  [coverage] No PRD found at $prd_path — skipping coverage analysis"
    return 1
  fi

  log "  [coverage] Analyzing test matrix coverage for M${m}..."

  # Extract test IDs from PRD stories
  local expected_ids
  expected_ids=$(_extract_milestone_test_ids "$prd_path")

  if [ -z "$expected_ids" ]; then
    log "  [coverage] No test IDs found in PRD stories — skipping"
    TEST_COVERAGE_REPORT="No test matrix IDs referenced in this milestone's PRD stories."
    return 0
  fi

  local expected_count
  expected_count=$(echo "$expected_ids" | wc -l)
  log "  [coverage] Found $expected_count test IDs in PRD"

  # Search codebase for implementations
  local found_ids
  found_ids=$(_find_implemented_test_ids "$expected_ids" "$PROJECT_ROOT")

  local found_count=0
  [ -n "$found_ids" ] && found_count=$(echo "$found_ids" | wc -l)

  local missing_count=$((expected_count - found_count))

  log "  [coverage] Results: $found_count/$expected_count implemented ($missing_count missing)"

  # Build structured report
  local report="TEST MATRIX COVERAGE ANALYSIS (automated by pipeline):
Expected tests: $expected_count | Found: $found_count | Missing: $missing_count

"

  if [ "$missing_count" -gt 0 ]; then
    report+="MISSING TEST IMPLEMENTATIONS (these are DEFECTS):
"
    local tid
    while IFS= read -r tid; do
      [ -z "$tid" ] && continue
      if ! echo "$found_ids" | grep -qxF "$tid"; then
        report+="  - $tid — NOT FOUND in codebase
"
      fi
    done <<< "$expected_ids"
    report+="
"
  fi

  if [ -n "$found_ids" ]; then
    report+="FOUND TEST IMPLEMENTATIONS:
"
    while IFS= read -r tid; do
      [ -z "$tid" ] && continue
      report+="  - $tid — found
"
    done <<< "$found_ids"
  fi

  TEST_COVERAGE_REPORT="$report"
  return 0
}

# ─── Phase 3: QA + Bugfix Cycles ─────────────────────────────────────────────

run_qa() {
  local m="$1"
  local slug
  slug=$(cfg_milestone_slug "$m")
  local branch="ralph/m${m}-${slug}"
  local prd_path="$TASKS_DIR/prd-m${m}.json"
  local qa_report="$QA_DIR/qa-m${m}-${slug}.md"

  log "Phase 3 (QA): M${m} (${slug})"

  mkdir -p "$QA_DIR"

  for cycle in $(seq 0 "$MAX_BUGFIX_CYCLES"); do
    if [ "$cycle" -gt 0 ]; then
      log "  Bugfix cycle $cycle for M${m}"
      run_ralph_bugfix "$m"
    fi

    log "  Running QA for M${m} (cycle $cycle)..."

    if [ "$DRY_RUN" = true ]; then
      log "  [DRY RUN] Would run QA for M${m}"
      return 0
    fi

    # Run test suite before QA — feed results as hard evidence
    run_test_suite "pre-QA M${m} cycle $cycle" "$PROJECT_ROOT" || true
    local qa_test_results="$TEST_OUTPUT"
    local qa_test_exit="$TEST_EXIT_CODE"
    store_test_results "$QA_DIR/test-results-qa-m${m}-cycle${cycle}.md" "QA M${m} cycle $cycle"

    local skill_content
    skill_content=$(cat "$SKILLS_DIR/qa_engineer/SKILL.md")

    local progress_path="$SCRIPT_DIR/progress.txt"

    # Build test results section for QA prompt
    local test_results_section=""
    if [ -n "$TEST_COMMAND" ]; then
      local test_status="PASS"
      [ "$qa_test_exit" -ne 0 ] && test_status="FAIL (exit code $qa_test_exit)"
      test_results_section="
TEST EXECUTION RESULTS (run by pipeline before QA):
Command: $TEST_COMMAND
Result: $test_status
Output (last 80 lines):
\`\`\`
$(echo "$qa_test_results" | tail -80)
\`\`\`

IMPORTANT: These test results are the ground truth. If tests fail, the failures are DEFECTS.
Tests verify acceptance criteria from the PRD — do NOT dismiss test failures."
    fi

    # Run test matrix coverage analysis
    local coverage_section=""
    if analyze_test_matrix_coverage "$m" "$prd_path"; then
      if [ -n "$TEST_COVERAGE_REPORT" ]; then
        coverage_section="
$TEST_COVERAGE_REPORT
IMPORTANT: Any test ID listed as MISSING above is a DEFECT. Ralph was required to implement these tests.
Include a 'Test Matrix Coverage' section in your QA report with the full FOUND/MISSING breakdown."
      fi
    fi

    # Check for test architecture docs
    local test_arch_ref=""
    if [ -d "$DOCS_DIR/04-test-architecture" ]; then
      test_arch_ref="
TEST ARCHITECTURE REFERENCE:
- Read $DOCS_DIR/04-test-architecture/test-matrix.md — verify Ralph wrote the specified tests
- Read $DOCS_DIR/04-test-architecture/runtime-safety.md — verify safety tests for loops, state machines, async
- The pipeline has already scanned the codebase for test IDs (see TEST MATRIX COVERAGE above)
- Cross-reference the automated scan results with your own code review"
    fi

    local prompt
    prompt="$skill_content

ARGUMENTS: Review milestone M${m} (${slug}).
Branch: $branch
PRD: $prd_path
Progress log: $progress_path
$test_results_section
$coverage_section
$test_arch_ref
Instructions:
- Read the PRD at $prd_path and the progress log at $progress_path
- Read ALL upstream docs (architecture, design, AI, milestones)
- Use the TEST EXECUTION RESULTS above as primary evidence for quality checks
- Use the TEST MATRIX COVERAGE above as primary evidence for test completeness — MISSING tests are DEFECTS
- Run additional quality checks: typecheck, lint, manual code review
- Produce a QA report at $qa_report
- Include a 'Test Matrix Coverage' section showing FOUND/MISSING per test ID
- Include a clear Verdict: PASS or Verdict: FAIL line
- If FAIL: describe exactly what failed, referencing test output and missing test IDs where applicable
- If FAIL and this is not the final cycle: update $prd_path — set passes=false on failing stories and add notes on what needs fixing"

    local output
    output=$(run_claude "$prompt" "$MODEL_QA" "qa_review" "$m") || {
      log "  WARNING: QA subprocess failed for M${m}"
    }

    local verdict
    verdict=$(extract_verdict "$qa_report")
    log "  QA verdict for M${m}: $verdict"

    if [ "$verdict" = "PASS" ]; then
      archive_milestone "$m"
      return 0
    fi

    if [ "$cycle" -eq "$MAX_BUGFIX_CYCLES" ]; then
      log "  ESCALATION: M${m} failed QA after $MAX_BUGFIX_CYCLES bugfix cycles"
      echo "# Escalation Report: M${m} (${slug})" > "$QA_DIR/escalation-m${m}-${slug}.md"
      echo "" >> "$QA_DIR/escalation-m${m}-${slug}.md"
      echo "Failed QA after $MAX_BUGFIX_CYCLES bugfix cycles." >> "$QA_DIR/escalation-m${m}-${slug}.md"
      echo "Last QA report: $qa_report" >> "$QA_DIR/escalation-m${m}-${slug}.md"
      echo "Timestamp: $(date -Iseconds)" >> "$QA_DIR/escalation-m${m}-${slug}.md"
      archive_milestone "$m"
      return 1
    fi
  done
}

# ─── Phase 4: Merge + Verify ─────────────────────────────────────────────────
# Merges milestone branch into base, runs heavy tests with fix cycles,
# then runs config-driven gate checks (typecheck, lint, docker build, etc.)

run_gate_checks() {
  GATE_ERRORS=""
  local gate_pass=true
  local num_checks
  num_checks=$(jq '.gate_checks.checks | length' "$CONFIG_FILE")

  cd "$PROJECT_ROOT"

  for i in $(seq 0 $((num_checks - 1))); do
    local check_name check_cmd check_cond check_required
    check_name=$(jq -r ".gate_checks.checks[$i].name" "$CONFIG_FILE")
    check_cmd=$(jq -r ".gate_checks.checks[$i].command" "$CONFIG_FILE")
    check_cond=$(jq -r ".gate_checks.checks[$i].condition" "$CONFIG_FILE")
    check_required=$(jq -r ".gate_checks.checks[$i].required" "$CONFIG_FILE")

    if [ -n "$check_cond" ] && ! eval "$check_cond" &>/dev/null; then
      log "  Skipping $check_name (condition not met)"
      continue
    fi

    log "  Running: $check_name"
    local check_out
    check_out=$(eval "$check_cmd" 2>&1) || {
      if [ "$check_required" = "true" ]; then
        gate_pass=false
        GATE_ERRORS+="=== $check_name FAILED ===
$(echo "$check_out" | tail -50)

"
        log "  FAILED: $check_name"
      else
        log "  WARNING: $check_name failed (non-required)"
      fi
      continue
    }
    log "  $check_name passed"
  done

  $gate_pass && return 0 || return 1
}

merge_and_verify() {
  local m="$1"
  local slug
  slug=$(cfg_milestone_slug "$m")
  local branch="ralph/m${m}-${slug}"

  log "Phase 4 (Merge+Verify): M${m} (${slug}) into $BASE_BRANCH"

  if [ "$DRY_RUN" = true ]; then
    log "  [DRY RUN] Would merge $branch into $BASE_BRANCH and verify"
    return 0
  fi

  cd "$PROJECT_ROOT"
  commit_dirty_tree "chore: pipeline artifacts after M${m} QA"

  # Safety: tag base branch before merge for rollback
  git checkout "$BASE_BRANCH"
  git tag "pre-m${m}-merge" 2>/dev/null || true

  # Dry-run conflict check
  if ! git merge --no-commit --no-ff "$branch" >/dev/null 2>&1; then
    git merge --abort 2>/dev/null || true
    log "  WARNING: Dry-run detected merge conflicts for $branch"
  else
    git merge --abort 2>/dev/null || true
  fi

  # Merge
  git merge "$branch" --no-ff -m "Merge M${m}: ${slug}" || {
    log "  Merge failed. Rolling back to pre-m${m}-merge"
    git merge --abort 2>/dev/null || true
    die "Merge conflict on M${m}. Resolve manually and resume with --milestone $m"
  }

  # Register test files from this milestone for regression analysis
  build_test_milestone_map "$m"

  # Heavy test enforcement — full test suite with auto-fix cycles (regression-aware)
  if ! run_test_fix_cycle "post-merge M${m}" "$PROJECT_ROOT" "$MAX_TEST_FIX_CYCLES" "$m"; then
    store_test_results "$QA_DIR/test-results-post-merge-m${m}.md" "Post-merge M${m}"
    die "Post-merge tests failed for M${m} after $MAX_TEST_FIX_CYCLES fix cycles. Fix manually and --resume."
  fi

  # Integration tests (if configured)
  if [ -n "$INTEGRATION_TEST_COMMAND" ] && [ "$INTEGRATION_TEST_COMMAND" != "null" ]; then
    log "  Running integration tests after merging M${m}..."
    local saved_test_cmd="$TEST_COMMAND"
    TEST_COMMAND="$INTEGRATION_TEST_COMMAND"
    if ! run_test_fix_cycle "integration M${m}" "$PROJECT_ROOT" "$MAX_TEST_FIX_CYCLES" "$m"; then
      store_test_results "$QA_DIR/test-results-integration-m${m}.md" "Integration M${m}"
      TEST_COMMAND="$saved_test_cmd"
      die "Integration tests failed after merging M${m}. Fix manually and --resume."
    fi
    TEST_COMMAND="$saved_test_cmd"
  fi

  # Config-driven gate checks with fix cycle
  for cycle in $(seq 0 "$MAX_GATE_FIX_CYCLES"); do
    if run_gate_checks; then
      log "  Gate checks PASSED for M${m}"
      break
    fi

    log "  Gate checks FAILED for M${m} (cycle $cycle)"

    if [ "$cycle" -eq "$MAX_GATE_FIX_CYCLES" ]; then
      log "  Gate errors:"
      log "$GATE_ERRORS"
      die "Gate checks failed after $MAX_GATE_FIX_CYCLES fix cycles for M${m}. Fix manually and --resume."
    fi

    log "  Invoking Claude to fix gate errors (cycle $((cycle + 1)))..."

    local prompt
    prompt="You are fixing build/typecheck errors on branch $BASE_BRANCH after merging M${m} ($slug).
Working directory: $PROJECT_ROOT

The following checks failed:

$GATE_ERRORS

Instructions:
- Read the failing files and fix the errors
- Only fix what is broken — do not refactor or add features
- Commit each fix with message: fix: gate check — <brief description>"

    run_claude "$prompt" "$MODEL_GATE_FIX" "gate_fix" "$m" || log "  WARNING: Claude fix attempt failed"
    commit_dirty_tree "fix: gate check fixes for M${m} (cycle $((cycle + 1)))"
  done

  # Tag successful merge+verify
  git tag "m${m}-complete"
  log "  M${m} merged, verified, and tagged m${m}-complete"

  # Clean up milestone branch
  git branch -d "$branch" 2>/dev/null || true
}

# ─── Phase 5: Spec Reconciliation ────────────────────────────────────────────

run_reconcile() {
  local m="$1"
  local slug
  slug=$(cfg_milestone_slug "$m")

  log "Phase 5 (Reconciliation): M${m} (${slug})"

  if [ "$DRY_RUN" = true ]; then
    log "  [DRY RUN] Would run Spec Reconciler for M${m}"
    return 0
  fi

  mkdir -p "$RECON_DIR"

  local skill_content
  skill_content=$(cat "$SKILLS_DIR/spec_reconciler/SKILL.md")

  local prompt
  prompt="$skill_content

ARGUMENTS: Reconcile specs after milestone M${m} (${slug}).

References:
- Archive: $ARCHIVE_DIR/m${m}-${slug}/
- QA report: $QA_DIR/qa-m${m}-${slug}.md

Instructions:
- Read progress file and QA report for M${m}
- Compare actual implementation against upstream spec docs
- Auto-apply ALL changes (pipeline trusts QA — no manual approval needed)
- Update spec docs to match reality where implementation deviated
- Record all changes in $RECON_DIR/m${m}-changes.md"

  cd "$PROJECT_ROOT"

  local changelog="$RECON_DIR/m${m}-changes.md"
  local attempt

  for attempt in 1 2; do
    run_claude "$prompt" "$MODEL_RECONCILIATION" "reconciliation" "$m" || {
      log "  WARNING: Spec Reconciler attempt $attempt failed for M${m}"
    }

    if [ -f "$changelog" ]; then
      commit_dirty_tree "docs: spec reconciliation after M${m}"
      log "  Reconciliation complete for M${m} (changelog: $changelog)"
      return 0
    fi

    if [ "$attempt" -eq 1 ]; then
      log "  Changelog not produced — retrying reconciliation (attempt 2)"
    fi
  done

  log "  WARNING: Spec Reconciler did not produce $changelog after 2 attempts — continuing"
  log "  Future milestone PRDs may reference stale specs. Consider running /spec_reconciler manually."
}

# ─── Phase Dispatcher ────────────────────────────────────────────────────────

phase_order() {
  case "$1" in
    prd_generation)   echo 1 ;;
    ralph_execution)  echo 2 ;;
    qa_review)        echo 3 ;;
    merge_verify)     echo 4 ;;
    reconciliation)   echo 5 ;;
    complete)         echo 6 ;;
    *)                echo 0 ;;
  esac
}

run_milestone() {
  local m="$1"
  local start_phase="${2:-prd_generation}"
  local start_order
  start_order=$(phase_order "$start_phase")
  local slug
  slug=$(cfg_milestone_slug "$m")
  local name
  name=$(cfg_milestone_name "$m")

  log "============================================================"
  log "  MILESTONE M${m}: ${name} (${slug}) START (from phase: $start_phase)"
  log "============================================================"

  if [ "$(phase_order prd_generation)" -ge "$start_order" ]; then
    save_state "$m" "prd_generation"
    generate_prd "$m"
  fi

  if [ "$(phase_order ralph_execution)" -ge "$start_order" ]; then
    save_state "$m" "ralph_execution"
    run_ralph "$m"
  fi

  if [ "$(phase_order qa_review)" -ge "$start_order" ]; then
    save_state "$m" "qa_review"
    run_qa "$m"
  fi

  if [ "$(phase_order merge_verify)" -ge "$start_order" ]; then
    save_state "$m" "merge_verify"
    merge_and_verify "$m"
  fi

  if [ "$(phase_order reconciliation)" -ge "$start_order" ]; then
    save_state "$m" "reconciliation"
    run_reconcile "$m"
  fi

  save_state "$m" "complete"
  log "MILESTONE M${m} COMPLETE"
  log ""
}

# ─── CLI Parsing & Main Execution ─────────────────────────────────────────────
if $_PIPELINE_SOURCED; then return 0; fi

START_MILESTONE=""
START_PHASE="prd_generation"
DRY_RUN=false
RESUME=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --config)
      CONFIG_FILE="$2"
      shift 2
      ;;
    --config=*)
      CONFIG_FILE="${1#*=}"
      shift
      ;;
    --resume)
      RESUME=true
      shift
      ;;
    --milestone)
      START_MILESTONE="$2"
      shift 2
      ;;
    --milestone=*)
      START_MILESTONE="${1#*=}"
      shift
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --help|-h)
      cat <<'HELPEOF'
Usage: pipeline.sh --config <path> [OPTIONS]

Required:
  --config <path>    Path to pipeline-config.json

Options:
  --resume           Resume from saved state in pipeline-state.json
  --milestone N      Start from milestone N (by ID)
  --dry-run          Show what would happen without executing
  --help, -h         Show this help

The config file defines milestones, gate checks, and all
project-specific settings. Generate it with /pipeline_configurator.
HELPEOF
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Run: pipeline.sh --help"
      exit 1
      ;;
  esac
done

# ─── Startup ──────────────────────────────────────────────────────────────────

[ -n "$CONFIG_FILE" ] || die "No config file specified. Use: pipeline.sh --config <path>"

if [[ "$CONFIG_FILE" != /* ]]; then
  CONFIG_FILE="$PROJECT_ROOT/$CONFIG_FILE"
fi

load_config
setup_env

# Validate required scripts exist
[ -f "$SCRIPT_DIR/ralph.sh" ] || die "ralph.sh not found at $SCRIPT_DIR/ralph.sh"

# ─── Clean Working Tree Check ─────────────────────────────────────────────────

cd "$PROJECT_ROOT"
if ! git diff --quiet HEAD 2>/dev/null || [ -n "$(git ls-files --others --exclude-standard)" ]; then
  log ""
  log "ERROR: Working tree is not clean on branch '$BASE_BRANCH'."
  log "Uncommitted changes detected:"
  git status --short | head -20 | while IFS= read -r line; do log "  $line"; done
  log ""
  die "Please commit or stash your changes before running the pipeline."
fi

# ─── Resume Logic ─────────────────────────────────────────────────────────────

if [ "$RESUME" = true ]; then
  if [ ! -f "$STATE_FILE" ]; then
    die "No state file found at $STATE_FILE — cannot resume"
  fi
  read -r saved_milestone saved_phase <<< "$(load_state)"
  START_MILESTONE="$saved_milestone"
  if [ "$saved_phase" = "complete" ]; then
    # Find next milestone after the completed one
    START_MILESTONE=$(python3 -c "
import json
cfg = json.load(open('$CONFIG_FILE'))
ids = [m['id'] for m in cfg['milestones']]
current = $saved_milestone
idx = ids.index(current) if current in ids else -1
if idx >= 0 and idx + 1 < len(ids):
    print(ids[idx + 1])
else:
    print(-1)
")
    if [ "$START_MILESTONE" = "-1" ]; then
      log "All milestones already complete."
      exit 0
    fi
    START_PHASE="prd_generation"
  else
    START_PHASE="$saved_phase"
  fi

  saved_branch="$(load_state_branch)"
  if [ -n "$saved_branch" ]; then
    if [ "$BASE_BRANCH" != "$saved_branch" ]; then
      log "WARNING: Current branch ($BASE_BRANCH) differs from saved base branch ($saved_branch)"
      log "Restoring base branch to: $saved_branch"
      BASE_BRANCH="$saved_branch"
    fi
  fi

  log "Resuming from Milestone $START_MILESTONE, phase $START_PHASE (base branch: $BASE_BRANCH)"
fi

# ─── Main Loop ────────────────────────────────────────────────────────────────

log ""
log "============================================================"
log "  PIPELINE START"
log "  Project: $(jq -r '.project.name' "$CONFIG_FILE")"
log "  Config: $CONFIG_FILE"
log "  Base branch: $BASE_BRANCH"
log "  Dry run: $DRY_RUN"
log "  Total milestones: $TOTAL_MILESTONES"
log "============================================================"
log ""

# Determine which milestones to run
MILESTONE_IDS=$(cfg_milestone_ids)
STARTED=false

for m in $MILESTONE_IDS; do
  # Skip milestones before the start milestone
  if [ -n "$START_MILESTONE" ] && [ "$STARTED" = false ]; then
    if [ "$m" -eq "$START_MILESTONE" ]; then
      STARTED=true
      run_milestone "$m" "$START_PHASE"
    fi
    continue
  fi

  # For milestones after the start, or if no start specified
  if [ -z "$START_MILESTONE" ] && [ "$STARTED" = false ]; then
    STARTED=true
  fi

  run_milestone "$m" "prd_generation"
done

# Clean up test infrastructure
teardown_test_infra

log ""
log "============================================================"
log "  PIPELINE COMPLETE — all $TOTAL_MILESTONES milestones finished"
log "============================================================"
