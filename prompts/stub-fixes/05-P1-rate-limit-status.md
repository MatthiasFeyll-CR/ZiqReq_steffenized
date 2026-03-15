# P1: Rate Limit Status — Always Returns Unlocked

## Goal

Per requirement F-2.11, there's an admin-configurable chat message cap per idea (default: 5). When the cap is reached without the AI completing a processing cycle, chat input should lock for all users on that idea. The counter resets when AI completes processing.

Both the Gateway and AI CoreClient `get_rate_limit_status` methods are stubs that always return `{"current_count": 0, "cap": 100, "is_locked": False}`, meaning rate limiting never activates.

## Files to Modify

### Gateway CoreClient:
- `services/gateway/grpc_clients/core_client.py` line ~148-150
  ```python
  def get_rate_limit_status(self, idea_id: str) -> dict[str, Any]:
      logger.warning("CoreClient.get_rate_limit_status stub called")
      return {"current_count": 0, "cap": 100, "is_locked": False}
  ```

### AI CoreClient:
- `services/ai/grpc_clients/core_client.py` line ~100-102
  ```python
  def get_rate_limit_status(self, idea_id: str) -> dict[str, Any]:
      logger.warning("AI CoreClient.get_rate_limit_status stub called")
      return {"current_count": 0, "cap": 100, "is_locked": False}
  ```

### Admin parameter:
- The `chat_message_cap` parameter should exist in admin config. Check:
  - `services/core/apps/admin_config/migrations/0001_create_admin_parameters_table.py`
  - `services/core/apps/admin_config/migrations/0002_seed_parameters.py`
  - Use `get_parameter("chat_message_cap", default=5, cast=int)` from `apps.admin_config.services`

### Chat message model:
- `services/core/apps/ideas/models.py` or `services/core/apps/chat/models.py` — `ChatMessage` model

### WebSocket consumer (rate limit enforcement):
- `services/gateway/apps/websocket/consumers.py` — check if there's rate limit checking on incoming chat messages

### AI processing complete handler (counter reset):
- `services/gateway/events/consumers.py` line ~213-225 — `_handle_processing_complete`
  Comment says: "Rate limiting is now handled by querying unprocessed messages in the DB, so no explicit counter reset is needed here."

## Implementation Logic

The rate limit works by counting unprocessed user messages since the last AI processing cycle:

1. **`current_count`**: Count user chat messages (`sender_type='user'`) for the idea that were created AFTER the last AI message (or after the last `ai.processing.complete` event). This can be derived from:
   ```sql
   SELECT COUNT(*) FROM chat_messages
   WHERE idea_id = %s AND sender_type = 'user'
   AND created_at > COALESCE(
       (SELECT MAX(created_at) FROM chat_messages
        WHERE idea_id = %s AND sender_type = 'ai'),
       '1970-01-01'
   )
   ```

2. **`cap`**: Read from admin parameter `chat_message_cap` (default: 5)

3. **`is_locked`**: `current_count >= cap`

## Proto Contract

```protobuf
message RateLimitRequest {
  string idea_id = 1;
}

message RateLimitResponse {
  int32 current_count = 1;
  int32 cap = 2;
  bool is_locked = 3;
}
```

## Related Requirements

- **F-2.11:** Rate Limiting — Admin-configurable chat message cap per idea (default: 5). If the cap is reached without the AI completing a processing cycle, chat input is locked for all users on that idea. Board remains editable — only chat is locked. Counter resets when AI completes processing. Cap is per idea, shared across all users.

## Consumers of This Data

- Frontend chat input component — disables input when `is_locked` is true
- WebSocket consumer — should reject new chat messages when locked
- AI processing pipeline — checks before processing
- Frontend shows "Locked out (rate cap reached)" warning toast (F-12.5)
