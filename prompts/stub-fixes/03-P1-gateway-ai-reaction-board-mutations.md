# P1: Gateway CoreClient — persist_ai_reaction & persist_board_mutations

## Goal

Two Gateway CoreClient methods silently discard AI-generated data:

1. **`persist_ai_reaction`** — When the AI reacts to a user message with a thumbs-up, thumbs-down, or heart emoji (requirement F-2.7), the reaction is never saved to the database. The method returns `{"reaction_id": ""}` and does nothing.

2. **`persist_board_mutations`** — When the AI modifies the digital board (creating/updating/deleting nodes and connections per F-2.17), those mutations are never persisted. The method returns `{"success": True, "mutations_applied": 0}` and does nothing. The mutations are broadcast via WebSocket but lost on page refresh.

## Files to Modify

### Primary file:
- `services/gateway/grpc_clients/core_client.py`
  - `persist_ai_reaction()` at line ~59-63
  - `persist_board_mutations()` at line ~79-83

### Current stub code:
```python
def persist_ai_reaction(self, idea_id: str, message_id: str, reaction_type: str) -> dict[str, Any]:
    logger.warning("CoreClient.persist_ai_reaction stub called")
    return {"reaction_id": ""}

def persist_board_mutations(self, idea_id: str, mutations: list[dict[str, Any]]) -> dict[str, Any]:
    logger.warning("CoreClient.persist_board_mutations stub called")
    return {"success": True, "mutations_applied": 0}
```

### Database models:
- `services/core/apps/ideas/models.py` — look for a `Reaction` or `ChatReaction` model
- `services/core/apps/board/models.py` — `BoardNode` and `BoardConnection` models
- `services/core/apps/chat/models.py` — may contain reaction model

### Reference: AI CoreClient has working board operations
- `services/ai/grpc_clients/core_client.py` lines 106-346 has fully working implementations for:
  - `create_board_node()`, `update_board_node()`, `delete_board_node()`
  - `move_board_node()`, `resize_board_group()`
  - `create_board_connection()`, `update_board_connection()`, `delete_board_connection()`
  These use raw SQL via `from django.db import connection`. The Gateway version can follow the same pattern or use Django ORM.

### Reference: Working Gateway CoreClient methods
- `persist_ai_chat_message()` at lines 35-57 is already implemented using Django ORM (`ChatMessage.objects.create(...)`)
- `update_idea_title()` at lines 65-77 is already implemented
- Follow the same ORM pattern for consistency

## What Each Method Should Do

### `persist_ai_reaction(idea_id, message_id, reaction_type)`
- `reaction_type` is one of: `"thumbs_up"`, `"thumbs_down"`, `"heart"`
- Create a reaction record linking the AI (sender_type="ai") to the target message
- First check if the chat message exists and belongs to the idea
- Return `{"reaction_id": "<uuid>"}` with the created reaction's ID

### `persist_board_mutations(idea_id, mutations: list[dict])`
- `mutations` is a list of dicts, each with a `type` field indicating the operation
- Mutation types (from `proto/core.proto` BoardMutation message):
  - `type`: operation type (e.g., "create_node", "update_node", "delete_node", "create_connection", etc.)
  - `node_id`, `content`, `node_type`, `x_position`, `y_position`, `parent_id`
  - `source_node_id`, `target_node_id`, `label` (for connections)
- Apply each mutation to the `board_nodes` or `board_connections` table
- Return `{"success": True, "mutations_applied": <count>}`

## Consumer: AI Event Consumer

The `services/gateway/events/consumers.py` `AIEventConsumer` class calls these methods:

```python
# Line 143 — reaction handler
result = self._core_client.persist_ai_reaction(
    idea_id=idea_id, message_id=message_id, reaction_type=reaction_type
)

# Line 82-83 in _handle_board_updated — NOTE: board mutations are currently
# only broadcast, not persisted through this path. Check if persist_board_mutations
# should be called here too.
```

## Proto Contract (for reference)

```protobuf
message AiReactionRequest {
  string idea_id = 1;
  string message_id = 2;
  string reaction_type = 3;
}

message AiReactionResponse {
  string reaction_id = 1;
}

message BoardMutationsRequest {
  string idea_id = 1;
  repeated BoardMutation mutations = 2;
}

message BoardMutation {
  string type = 1;
  string node_id = 2;
  string content = 3;
  string node_type = 4;
  double x_position = 5;
  double y_position = 6;
  string parent_id = 7;
  string source_node_id = 8;
  string target_node_id = 9;
  string label = 10;
}
```

## Gotchas
- The AI CoreClient's board operations use raw SQL. The Gateway CoreClient's existing methods use Django ORM. Stay consistent with Gateway conventions (ORM).
- The `_handle_board_updated` handler in `events/consumers.py` currently only broadcasts via WebSocket without calling `persist_board_mutations`. You may need to add the persist call there too.
