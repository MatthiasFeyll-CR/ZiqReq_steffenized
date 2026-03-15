# P2: Facilitator & Context Agent Bucket Servicer Stubs

## Goal

The AI context servicer at `services/ai/grpc_server/servicers/context_servicer.py` has 3 out of 4 methods returning empty placeholder data. Only `UpdateContextAgentBucket` actually works (persists to DB and triggers embedding pipeline). The other three need real implementations.

This means:
- Admins editing the **Facilitator context** in the Admin Panel (F-2.16) → changes are silently lost
- Reading Facilitator or Context Agent bucket contents via the Admin Panel → returns empty strings
- The AI Facilitator agent can't access its company context table of contents

## Files to Modify

### Primary file:
- `services/ai/grpc_server/servicers/context_servicer.py`

### Current stub methods:
```python
def GetFacilitatorBucket(self, request, context):
    return {"id": "", "content": "", "updated_by_id": "", "updated_at": ""}

def UpdateFacilitatorBucket(self, request, context):
    return {"id": "", "content": "", "updated_by_id": "", "updated_at": ""}

def GetContextAgentBucket(self, request, context):
    return {"id": "", "sections_json": "{}", "free_text": "", "updated_by_id": "", "updated_at": ""}
```

### Working reference — `UpdateContextAgentBucket` (same file, line 30-98):
This method already works correctly. It:
1. Reads `sections_json` and `free_text` from the request
2. Gets or creates a `ContextAgentBucket` from `apps.context.models`
3. Saves to DB
4. Triggers `Reindexer().reindex()` for embedding pipeline
5. Returns result with chunk_count, total_tokens, duration_ms

### Models:
- `ContextAgentBucket` — imported from `apps.context.models` in the working method
- Look for a `FacilitatorBucket` model in the same module or nearby
- If no `FacilitatorBucket` model exists, check what the Gateway AI client expects and create one

### Gateway AI client (the consumer):
- `services/gateway/grpc_clients/ai_client.py` — has methods:
  - `get_facilitator_bucket()` (line ~84-86) — calls `stub.GetFacilitatorBucket(Empty())`
  - `update_facilitator_bucket()` (line ~97-102) — calls `stub.UpdateFacilitatorBucket(request)`
  - `get_context_agent_bucket()` (line ~111-113) — calls `stub.GetContextAgentBucket(Empty())`
  - `update_context_agent_bucket()` (line ~125-131) — calls `stub.UpdateContextAgentBucket(request)`

### Admin Panel frontend:
- `frontend/src/features/admin/AIContextTab.tsx` — the admin UI for editing both buckets

## Proto Contract

```protobuf
// From proto/ai.proto
rpc GetFacilitatorBucket(google.protobuf.Empty) returns (FacilitatorBucketResponse);
rpc UpdateFacilitatorBucket(UpdateFacilitatorBucketRequest) returns (FacilitatorBucketResponse);
rpc GetContextAgentBucket(google.protobuf.Empty) returns (ContextAgentBucketResponse);
rpc UpdateContextAgentBucket(UpdateContextAgentBucketRequest) returns (ContextAgentBucketResponse);

message FacilitatorBucketResponse {
  string id = 1;
  string content = 2;
  string updated_by_id = 3;
  string updated_at = 4;
}

message UpdateFacilitatorBucketRequest {
  string content = 1;
  string updated_by_id = 2;
}

message ContextAgentBucketResponse {
  string id = 1;
  string sections_json = 2;
  string free_text = 3;
  string updated_by_id = 4;
  string updated_at = 5;
}
```

## Implementation

### `GetFacilitatorBucket`
- Query the FacilitatorBucket model (or equivalent) — likely a single-row table
- Return `{id, content, updated_by_id, updated_at}` from the DB record
- If no record exists, return empty strings (current behavior, but from DB not hardcoded)

### `UpdateFacilitatorBucket`
- Get or create the FacilitatorBucket record
- Update `content` and `updated_by_id` from request
- Save to DB
- Return the updated record as `FacilitatorBucketResponse`
- NOTE: Unlike UpdateContextAgentBucket, this does NOT need to trigger the embedding pipeline — the facilitator bucket is just a table of contents, not searchable content

### `GetContextAgentBucket`
- Query the ContextAgentBucket model (already used by `UpdateContextAgentBucket`)
- Return `{id, sections_json, free_text, updated_by_id, updated_at}`
- `sections_json` should be `json.dumps(bucket.sections)` since the model stores it as a dict

## Related Requirements

- **F-2.15:** Company Context Awareness — AI has access to company business context
- **F-2.16:** Company Context Management — Admins maintain company context through Admin Panel. Two areas: high-level table of contents (Facilitator bucket) and detailed sections + free text (Context Agent bucket)
- **F-11.2:** AI Context Tab — Two isolated areas in admin panel for facilitator context and detailed company context
