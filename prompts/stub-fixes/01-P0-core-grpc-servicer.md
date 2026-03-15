# P0: Core gRPC Servicer — Dead Code / Architectural Decision

## Goal

The Core service has a gRPC servicer at `services/core/grpc_server/servicers/core_servicer.py` that implements every RPC method from `proto/core.proto` — but ALL methods return hardcoded placeholder data and never touch the database. Meanwhile, the actual consumers (Gateway CoreClient, AI CoreClient) either bypass gRPC entirely via direct Django ORM queries or return stubs themselves.

**Decision required:** Either (a) wire up real gRPC calls end-to-end, or (b) commit to the direct-DB approach and remove the dead gRPC servicer. Option (b) is recommended since the Gateway and AI services already share the same Django database and the direct-DB clients are partially implemented.

If choosing option (b): remove the stub servicer, clean up any gRPC server startup code that references it, and ensure all CoreClient methods across services use direct DB access.

If choosing option (a): implement all 11 RPC methods in the servicer to query the real database, then update all CoreClient classes to make actual gRPC calls instead of direct DB access.

## Files to Modify

### The stub servicer (all methods return fake data):
- `services/core/grpc_server/servicers/core_servicer.py` — 11 methods, all returning hardcoded dicts

### The gRPC proto contract:
- `proto/core.proto` — defines `CoreService` with these RPCs:
  - `GetIdeaContext(IdeaContextRequest) returns (IdeaContextResponse)`
  - `GetFullChatHistory(FullChatHistoryRequest) returns (FullChatHistoryResponse)`
  - `PersistAiChatMessage(AiChatMessageRequest) returns (AiChatMessageResponse)`
  - `PersistAiReaction(AiReactionRequest) returns (AiReactionResponse)`
  - `UpdateIdeaTitle(UpdateTitleRequest) returns (UpdateTitleResponse)`
  - `PersistBoardMutations(BoardMutationsRequest) returns (BoardMutationsResponse)`
  - `UpdateBrdDraft(UpdateBrdDraftRequest) returns (UpdateBrdDraftResponse)`
  - `UpdateIdeaKeywords(UpdateKeywordsRequest) returns (UpdateKeywordsResponse)`
  - `GetIdeasByState(IdeasByStateRequest) returns (IdeasByStateResponse)`
  - `GetUserStats(GetUserStatsRequest) returns (UserStatsResponse)`
  - `GetRateLimitStatus(RateLimitRequest) returns (RateLimitResponse)`

### CoreClient implementations that consume this service:
- `services/gateway/grpc_clients/core_client.py` — Gateway's CoreClient (hybrid: some direct DB, some stubs)
- `services/ai/grpc_clients/core_client.py` — AI's CoreClient (hybrid: board ops via direct DB, rest stubs)
- `services/notification/grpc_clients/core_client.py` — Notification's CoreClient (fully stubbed, 1 method)

### Django models the servicer should query:
- `services/core/apps/ideas/models.py` — `Idea`, `ChatMessage` models
- `services/core/apps/board/models.py` — `BoardNode`, `BoardConnection` models
- `services/core/apps/brd/models.py` — `BrdDraft` model
- `services/core/apps/chat/models.py` — chat-related models
- `services/core/apps/review/models.py` — review models

### gRPC server startup (check for registration code):
- Look in `services/core/grpc_server/` for server.py or similar that registers the servicer

## Current State of the Stub

Every method in `core_servicer.py` returns a hardcoded dict. Examples:
```python
def GetIdeaContext(self, request, context):
    return {
        "metadata": {"idea_id": "", "title": "", ...},
        "recent_messages": [],
        "board": {"nodes": [], "connections": []},
        ...
    }

def PersistBoardMutations(self, request, context):
    return {"success": True, "mutations_applied": 0}
```

## Context: How the AI CoreClient Already Does Direct DB

The AI service's `CoreClient.get_idea_context()` (lines 21-89 of `services/ai/grpc_clients/core_client.py`) already uses `from django.db import connection` with raw SQL to query `ideas`, `chat_messages`, `chat_context_summaries`, `board_nodes`, `board_connections` tables directly. This is the pattern to follow if choosing option (b).

## Architecture Note

All services (gateway, core, ai) share the same PostgreSQL database. The gRPC layer was designed as an abstraction boundary, but the vibe-coding process resulted in services bypassing it. Whichever approach you choose, make it consistent across all three CoreClient implementations.
