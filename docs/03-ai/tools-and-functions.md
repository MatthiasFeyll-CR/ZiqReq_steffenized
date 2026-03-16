# Tools & Function Definitions

> **Status:** Definitive. Exact schemas for all 6 Semantic Kernel plugins.
>
> **Date:** 2026-03-16
> **Author:** AI Engineer (Refactored for requirements assembly platform)
> **Input:** `docs/03-ai/agent-architecture.md`, `docs/03-ai/system-prompts.md`, `REFACTORING_PLAN.md`

---

## Overview

Only the Facilitator agent uses Semantic Kernel function calling (tools). All other agents are simple chat completion with no tools.

| Agent | Plugin Count | Tools |
|-------|-------------|-------|
| Facilitator (Requirements Assistant) | 1 plugin, 6 functions | send_chat_message, react_to_message, update_title, delegate_to_context_agent, delegate_to_context_extension, update_requirements_structure |

**Removed from previous design:**
- **Board Agent plugin** — 8 tools (Board/canvas functionality eliminated)
- **request_board_changes tool** — Replaced by update_requirements_structure

**Schema format:** OpenAI function calling format (what the model sees). Semantic Kernel translates its plugin definitions to this format when communicating with Azure OpenAI.

**Implementation:** Each plugin is a Python class in the agent's `plugins.py` file. SK's `@kernel_function` decorator registers methods as callable functions. The schemas below define the contract between the model and the plugin implementation.

---

## Facilitator Plugin

### Plugin Registration

```python
# services/ai/agents/facilitator/plugins.py
class FacilitatorPlugin:
    """Tools for the Facilitator AI to interact with the project workspace."""
```

---

### 1. send_chat_message

Posts an AI chat message to the project's conversation.

**Function Definition:**

```json
{
  "name": "send_chat_message",
  "description": "Send a chat message to the project's conversation. Use this to respond to users, ask clarifying questions, or post delegation messages. Use natural conversational language.",
  "parameters": {
    "type": "object",
    "properties": {
      "content": {
        "type": "string",
        "description": "The message text. Use natural conversational language. When discussing requirements structure items, refer to them by title or description, not by ID."
      },
      "message_type": {
        "type": "string",
        "enum": ["regular", "delegation"],
        "description": "Message type. Use 'regular' for normal responses. Use 'delegation' ONLY for the brief message sent before a context agent or context extension delegation (e.g., 'Let me look into that...'). Delegation messages are visually de-emphasized after the real response arrives.",
        "default": "regular"
      }
    },
    "required": ["content"]
  }
}
```

**Return Schema:**

```json
{
  "type": "object",
  "properties": {
    "message_id": {
      "type": "string",
      "format": "uuid",
      "description": "The ID of the created chat message"
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "Timestamp of creation"
    }
  }
}
```

**Error Cases:**

| Error | Condition | Behavior |
|-------|-----------|----------|
| `project_locked` | Project is in a read-only state (accepted, dropped) | Return error. Facilitator should not have been triggered. |
| `rate_limited` | Chat is locked due to rate limit cap | Return error. Processing should not have started. |

**Implementation Notes:**
- The plugin publishes an `ai.chat_response.ready` event to the message broker.
- The gateway receives the event, persists the message via core service gRPC, and broadcasts via WebSocket.
- **No board item references:** The `[[Board Item Title]]` syntax from the old design is removed.

---

### 2. react_to_message

Places an AI reaction on a user's chat message.

**Function Definition:**

```json
{
  "name": "react_to_message",
  "description": "Place a reaction on a specific user message. Use thumbs_up to acknowledge a message without responding ('I've seen this, nothing to add'). Use thumbs_down to signal disagreement (prefer a written response instead). Use heart to signal 'your answer fully clarified my question'. Only react to USER messages, never to AI messages.",
  "parameters": {
    "type": "object",
    "properties": {
      "message_id": {
        "type": "string",
        "format": "uuid",
        "description": "The ID of the user message to react to. Must be a message with sender_type 'user'."
      },
      "reaction_type": {
        "type": "string",
        "enum": ["thumbs_up", "thumbs_down", "heart"],
        "description": "The reaction to place. thumbs_up = acknowledged, nothing to add. thumbs_down = disagreement. heart = your answer fully clarified my question."
      }
    },
    "required": ["message_id", "reaction_type"]
  }
}
```

**Return Schema:**

```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean",
      "description": "Whether the reaction was placed successfully"
    }
  }
}
```

**Error Cases:**

| Error | Condition | Behavior |
|-------|-----------|----------|
| `invalid_message` | message_id does not exist or is an AI message | Return error with description. Model should not react to AI messages. |
| `already_reacted` | AI already has a reaction on this message | Return error. One AI reaction per message max. |

**Implementation Notes:**
- Validates that `chat_messages.sender_type = 'user'` for the target message.
- Publishes `ai.reaction.ready` event.
- Enforces the unique constraint: one AI reaction per message (uq_ai_reaction_per_message).

---

### 3. update_title

Updates the project's title. Only callable when `title_manually_edited` is false.

**Function Definition:**

```json
{
  "name": "update_title",
  "description": "Update the project's title. Generate a short, concise title (under 60 characters) that reflects the current direction of the requirements. Call this when the project is new (first title) or when the existing title no longer fits because the scope has evolved. Do NOT call this if the system prompt indicates the title was manually edited.",
  "parameters": {
    "type": "object",
    "properties": {
      "title": {
        "type": "string",
        "maxLength": 60,
        "description": "The new title. Must be under 60 characters. Should be concise and descriptive of the project's core objective."
      }
    },
    "required": ["title"]
  }
}
```

**Return Schema:**

```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean"
    },
    "title": {
      "type": "string",
      "description": "The title as saved (may be truncated if over limit)"
    }
  }
}
```

**Error Cases:**

| Error | Condition | Behavior |
|-------|-----------|----------|
| `title_locked` | `title_manually_edited` is true | Return error. The system prompt should prevent this call, but the plugin enforces it as a safety net. |

**Implementation Notes:**
- Publishes `ai.title.updated` event.
- Gateway broadcasts title change via WebSocket. Browser tab title updates dynamically (F-1.8).
- Title change is animated on the frontend (F-2.3).

---

### 4. delegate_to_context_agent

Triggers a delegation to the Context Agent for company-specific information retrieval.

**Function Definition:**

```json
{
  "name": "delegate_to_context_agent",
  "description": "Delegate to the Context Agent to retrieve company-specific information from the knowledge base. Call this when the user's message relates to a topic requiring company context (systems, processes, org structure, domain terminology). IMPORTANT: Before calling this, you should first call send_chat_message with message_type 'delegation' to inform the user you are looking something up.",
  "parameters": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "A precise description of what company information is needed. Be specific: 'What document management system does Commerz Real use and which departments use it?' is better than 'Tell me about documents'."
      }
    },
    "required": ["query"]
  }
}
```

**Return Schema:**

```json
{
  "type": "object",
  "properties": {
    "delegation_id": {
      "type": "string",
      "format": "uuid",
      "description": "ID of the delegation request. Results will be delivered asynchronously."
    },
    "status": {
      "type": "string",
      "enum": ["queued"],
      "description": "The delegation has been queued for processing."
    }
  }
}
```

**Asynchronous Flow:**

This tool is **non-blocking**. After the Facilitator calls it:
1. The delegation request is published as an event.
2. The Context Agent processes the request (RAG retrieval + generation).
3. The pipeline orchestrator triggers a second Facilitator invocation with the Context Agent's findings injected as `<delegation_results>`.
4. The Facilitator generates a contextualized response using the findings.
5. The original delegation message is de-emphasized via a WebSocket event.

The Facilitator does NOT wait for results in the same invocation. The SK function calling loop returns after this tool call, and the pipeline orchestrator handles the continuation.

**Error Cases:**

| Error | Condition | Behavior |
|-------|-----------|----------|
| `context_bucket_empty` | The context agent bucket has no content | Return error. The Facilitator should respond without company context. |

**Implementation Notes:**
- Publishes `ai.delegation.started` event.
- The pipeline orchestrator (`processing/pipeline.py`) handles the async continuation.
- If the Context Agent fails, the orchestrator publishes `ai.delegation.complete` with empty findings, and the Facilitator responds based on general context.

---

### 5. delegate_to_context_extension

Triggers a delegation to the Context Extension Agent for full chat history search.

**Function Definition:**

```json
{
  "name": "delegate_to_context_extension",
  "description": "Delegate to the Context Extension Agent to search the full, uncompressed chat history. Call this when the user references a specific detail from earlier in the conversation that you cannot find in the compressed summary or recent messages. IMPORTANT: Before calling this, you should first call send_chat_message with message_type 'delegation' to inform the user you are looking back through the conversation. Do NOT call this if no compressed context exists (all messages are already visible in recent_messages).",
  "parameters": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "A precise description of what conversation detail to find. Be specific: 'What did Lisa say about the approval workflow requirements?' is better than 'What was discussed earlier?'."
      }
    },
    "required": ["query"]
  }
}
```

**Return Schema:**

```json
{
  "type": "object",
  "properties": {
    "delegation_id": {
      "type": "string",
      "format": "uuid",
      "description": "ID of the extension request. Results will be delivered asynchronously."
    },
    "status": {
      "type": "string",
      "enum": ["queued"],
      "description": "The extension request has been queued for processing."
    }
  }
}
```

**Asynchronous Flow:**

Same pattern as `delegate_to_context_agent`:
1. The extension request is queued.
2. The pipeline orchestrator loads the full chat history via Core gRPC `GetFullChatHistory`.
3. The Context Extension Agent searches the full history and returns findings.
4. The pipeline orchestrator triggers a second Facilitator invocation with findings injected as `<extension_results>`.
5. The Facilitator generates a response with the retrieved detail.
6. The original delegation message is de-emphasized.

**Error Cases:**

| Error | Condition | Behavior |
|-------|-----------|----------|
| `no_compressed_context` | `chat_context_summaries` does not exist for this project (no compression has occurred) | Return error. All messages are already in the Facilitator's recent messages window — extension is unnecessary. |
| `history_unavailable` | Core gRPC `GetFullChatHistory` fails | Return error. Facilitator should respond: "I couldn't retrieve that detail from earlier." |

**Implementation Notes:**
- Publishes `ai.delegation.started` event (same event type as context agent delegation — the event payload includes `delegation_type: "context_extension"` to distinguish).
- The Context Extension Agent uses the Escalated model tier (larger context budget for full chat history).
- Timeout is 90s (1.5× `ai_processing_timeout`) to accommodate large chat histories.

---

### 6. update_requirements_structure

Outputs structured mutations to the requirements document structure.

**Function Definition:**

```json
{
  "name": "update_requirements_structure",
  "description": "Submit structured mutations to update the project's requirements. Use this when the conversation has produced enough detail to add new epics/milestones, user stories/work packages, or update existing ones. You can send multiple mutations in a single call. The mutations are processed in order. Only call this when you have substantial content from the conversation — don't create placeholder entries.",
  "parameters": {
    "type": "object",
    "properties": {
      "mutations": {
        "type": "array",
        "description": "List of structured mutations to apply to the requirements document. Each mutation describes a specific change.",
        "items": {
          "type": "object",
          "properties": {
            "operation": {
              "type": "string",
              "enum": [
                "add_epic", "update_epic", "remove_epic", "reorder_epics",
                "add_story", "update_story", "remove_story", "reorder_stories",
                "add_milestone", "update_milestone", "remove_milestone", "reorder_milestones",
                "add_package", "update_package", "remove_package", "reorder_packages"
              ],
              "description": "The type of mutation to apply. Epic/Story operations are for software projects. Milestone/Package operations are for non-software projects."
            },
            "data": {
              "type": "object",
              "description": "Operation-specific data. Schema varies by operation type (see detailed schemas below)."
            }
          },
          "required": ["operation", "data"]
        },
        "minItems": 1
      }
    },
    "required": ["mutations"]
  }
}
```

**Operation-Specific Data Schemas:**

#### add_epic (Software)
```json
{
  "title": "string (required, max 200 chars)",
  "description": "string (required, 2-4 paragraphs explaining the capability)"
}
```

#### update_epic (Software)
```json
{
  "epic_id": "string (required, existing epic ID)",
  "title": "string (optional, updates if provided)",
  "description": "string (optional, updates if provided)"
}
```

#### remove_epic (Software)
```json
{
  "epic_id": "string (required, existing epic ID)"
}
```
**Note:** Removing an epic also removes all its user stories.

#### reorder_epics (Software)
```json
{
  "epic_ids": ["array of epic IDs in desired order"]
}
```

#### add_story (Software)
```json
{
  "epic_id": "string (required, parent epic ID)",
  "title": "string (required, max 200 chars, should follow 'As a [role], I want [capability] so that [benefit]' format)",
  "description": "string (required, 1-2 paragraphs)",
  "acceptance_criteria": "string (required, bullet list of testable criteria)",
  "priority": "string (required, enum: 'High' | 'Medium' | 'Low')"
}
```

#### update_story (Software)
```json
{
  "story_id": "string (required, existing story ID)",
  "title": "string (optional)",
  "description": "string (optional)",
  "acceptance_criteria": "string (optional)",
  "priority": "string (optional, enum: 'High' | 'Medium' | 'Low')"
}
```

#### remove_story (Software)
```json
{
  "story_id": "string (required, existing story ID)"
}
```

#### reorder_stories (Software)
```json
{
  "epic_id": "string (required, parent epic ID)",
  "story_ids": ["array of story IDs in desired order"]
}
```

#### add_milestone (Non-Software)
```json
{
  "title": "string (required, max 200 chars)",
  "description": "string (required, 2-4 paragraphs explaining the phase/objective)"
}
```

#### update_milestone (Non-Software)
```json
{
  "milestone_id": "string (required, existing milestone ID)",
  "title": "string (optional)",
  "description": "string (optional)"
}
```

#### remove_milestone (Non-Software)
```json
{
  "milestone_id": "string (required, existing milestone ID)"
}
```
**Note:** Removing a milestone also removes all its work packages.

#### reorder_milestones (Non-Software)
```json
{
  "milestone_ids": ["array of milestone IDs in desired order"]
}
```

#### add_package (Non-Software)
```json
{
  "milestone_id": "string (required, parent milestone ID)",
  "title": "string (required, max 200 chars)",
  "description": "string (required, 1-2 paragraphs)",
  "deliverables": "string (required, bullet list of concrete deliverables)",
  "dependencies": "string (optional, what must be completed first or what this depends on)"
}
```

#### update_package (Non-Software)
```json
{
  "package_id": "string (required, existing package ID)",
  "title": "string (optional)",
  "description": "string (optional)",
  "deliverables": "string (optional)",
  "dependencies": "string (optional)"
}
```

#### remove_package (Non-Software)
```json
{
  "package_id": "string (required, existing package ID)"
}
```

#### reorder_packages (Non-Software)
```json
{
  "milestone_id": "string (required, parent milestone ID)",
  "package_ids": ["array of package IDs in desired order"]
}
```

**Return Schema:**

```json
{
  "type": "object",
  "properties": {
    "accepted": {
      "type": "boolean",
      "description": "Whether the mutations were accepted for processing"
    },
    "mutation_count": {
      "type": "integer",
      "description": "Number of mutations queued"
    },
    "mutations_applied": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "operation": { "type": "string" },
          "status": { "type": "string", "enum": ["success", "failed"] },
          "error": { "type": "string", "description": "Error message if status is failed" }
        }
      },
      "description": "Results of each mutation"
    }
  }
}
```

**Error Cases:**

| Error | Condition | Behavior |
|-------|-----------|----------|
| `project_locked` | Project is in read-only state | Return error. No mutations allowed. |
| `invalid_operation` | Operation doesn't match project_type (e.g., add_epic on non-software project) | Return error for that mutation. Other mutations may still succeed. |
| `item_not_found` | Referenced epic/milestone/story/package ID doesn't exist | Return error for that mutation. Other mutations may still succeed. |
| `item_locked` | Attempting to update/remove a locked item | Return error for that mutation. Skip that mutation. |
| `validation_error` | Required fields missing or invalid data | Return error for that mutation with validation details. |

**Implementation Notes:**
- Mutations are processed sequentially. If one fails, subsequent mutations are still attempted.
- Each successful mutation publishes an `ai.requirements.updated` event.
- IDs for new items (epics, milestones, stories, packages) are generated by the Core service and returned in the mutation results.
- The Facilitator can reference newly created items in subsequent mutations within the same call using the returned IDs.

**Example Usage:**

```json
{
  "mutations": [
    {
      "operation": "add_epic",
      "data": {
        "title": "User Authentication System",
        "description": "This epic covers all functionality for user registration, login, password management, and session handling. Users need to be able to create accounts with email verification, log in securely with multi-factor authentication options, reset forgotten passwords, and manage their profile information."
      }
    },
    {
      "operation": "add_story",
      "data": {
        "epic_id": "epic_001",
        "title": "As a new user, I want to register for an account so that I can access the system",
        "description": "New users need a registration form where they provide email, password, and basic profile information. After submission, they receive a verification email with a link to activate their account.",
        "acceptance_criteria": "- Registration form includes fields: email, password, confirm password, first name, last name\n- Password must meet complexity requirements (8+ chars, uppercase, lowercase, number)\n- Verification email sent within 2 minutes of registration\n- Account is inactive until email verification link is clicked\n- Confirmation message displayed after successful registration",
        "priority": "High"
      }
    }
  ]
}
```

---

## Error Response Format

All tool errors follow a consistent format returned to the model:

```json
{
  "error": {
    "code": "error_code_snake_case",
    "message": "Human-readable description of what went wrong and why.",
    "details": {}
  }
}
```

The model receives this as the tool call result and can decide how to proceed (retry with different parameters, skip the operation, or inform the user).

**Common error codes across all tools:**

| Code | Description |
|------|-------------|
| `project_locked` | The project is in a read-only state (accepted, dropped) |
| `rate_limited` | Chat input is locked due to rate limit cap |
| `context_bucket_empty` | The context agent bucket has no content for RAG retrieval |
| `no_compressed_context` | No chat compression has occurred — context extension is unnecessary |
| `history_unavailable` | Full chat history could not be retrieved from Core service |
| `validation_error` | Input parameters failed validation (details in error.details) |
| `item_not_found` | Referenced item ID (epic, milestone, story, package) doesn't exist |
| `item_locked` | Attempting to modify a locked item |
| `invalid_operation` | Operation doesn't match project type or current state |
| `title_locked` | Attempting to update a manually-edited title |
| `invalid_message` | Message ID doesn't exist or is the wrong type |
| `already_reacted` | AI already has a reaction on this message |

---

## SK Plugin Implementation Pattern

All plugins follow the same implementation pattern using Semantic Kernel decorators:

```python
from semantic_kernel.functions import kernel_function
from pydantic import BaseModel, Field

class UpdateRequirementsStructureInput(BaseModel):
    """Input schema for update_requirements_structure, validated by Pydantic."""
    mutations: list[dict] = Field(..., min_length=1)

class UpdateRequirementsStructureOutput(BaseModel):
    """Return schema for update_requirements_structure."""
    accepted: bool
    mutation_count: int
    mutations_applied: list[dict]

class FacilitatorPlugin:
    def __init__(self, project_id: str, core_client: CoreGrpcClient):
        self.project_id = project_id
        self.core_client = core_client

    @kernel_function(
        name="update_requirements_structure",
        description="Submit structured mutations to update the project's requirements..."
    )
    async def update_requirements_structure(
        self, input: UpdateRequirementsStructureInput
    ) -> UpdateRequirementsStructureOutput:
        # Validate project state
        # Process each mutation via Core gRPC
        # Publish ai.requirements.updated events
        # Return results
        ...
```

**Key patterns:**
- **Pydantic models** for input validation and output serialization.
- **gRPC calls** to the core service for all persistence operations.
- **Event publishing** for all mutations (consumed by gateway for WebSocket broadcast).
- **Error handling** catches gRPC errors and converts to the standard error response format.
- **Project context** (project_id, locked state) is injected at plugin initialization, not passed per call.

---

## Tool Execution Flow

### Facilitator — Multi-Turn Function Calling

The Facilitator uses SK's automatic function calling loop. In a single processing cycle, the model may call multiple tools across multiple turns:

```
Turn 1: Model decides to respond + update requirements structure + update title
  → calls send_chat_message(content="...")
  → calls update_title(title="...")
  → calls update_requirements_structure(mutations=[...])

Turn 2: Model receives results from all 3 calls
  → determines no further action needed
  → loop ends
```

Or with delegation:
```
Turn 1: Model decides to delegate to context agent
  → calls send_chat_message(content="Let me look into that...", message_type="delegation")
  → calls delegate_to_context_agent(query="...")

Turn 2: Model receives results
  → delegation is async, loop ends here
  → pipeline orchestrator handles continuation
```

Or with context extension:
```
Turn 1: Model decides to retrieve old conversation detail
  → calls send_chat_message(content="Let me check our earlier conversation...", message_type="delegation")
  → calls delegate_to_context_extension(query="...")

Turn 2: Model receives results
  → extension is async, loop ends here
  → pipeline orchestrator handles continuation
```

**SK configuration:**
- `max_auto_invoke_attempts`: 3 (maximum function calling rounds per cycle)
- `function_choice_behavior`: auto (model decides which functions to call)

---

## Validation Rules Summary

| Tool | Key Validations |
|------|----------------|
| send_chat_message | content is non-empty; project is not in read-only state |
| react_to_message | target message exists; target is a user message; no existing AI reaction on that message |
| update_title | title ≤ 60 chars; title_manually_edited is false |
| delegate_to_context_agent | query is non-empty; context agent bucket has content |
| delegate_to_context_extension | query is non-empty; compressed context exists for this project; Core gRPC reachable |
| update_requirements_structure | at least 1 mutation; operation matches project_type; item IDs valid; items not locked; required fields present |
