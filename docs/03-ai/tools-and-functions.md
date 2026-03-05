# Tools & Function Definitions

> **Status:** Definitive. Exact schemas for all 14 Semantic Kernel plugins.
>
> **Date:** 2026-03-02
> **Author:** AI Engineer (Phase 3b)
> **Input:** `docs/03-ai/agent-architecture.md`, `docs/03-ai/system-prompts.md`

---

## Overview

Two agents use Semantic Kernel function calling (tools). All other agents are simple chat completion with no tools.

| Agent | Plugin Count | Tools |
|-------|-------------|-------|
| Facilitator (Core) | 1 plugin, 6 functions | send_chat_message, react_to_message, update_title, delegate_to_context_agent, delegate_to_context_extension, request_board_changes |
| Board Agent | 1 plugin, 8 functions | create_node, update_node, delete_node, move_node, resize_group, create_connection, update_connection, delete_connection |

**Schema format:** OpenAI function calling format (what the model sees). Semantic Kernel translates its plugin definitions to this format when communicating with Azure OpenAI.

**Implementation:** Each plugin is a Python class in the agent's `plugins.py` file. SK's `@kernel_function` decorator registers methods as callable functions. The schemas below define the contract between the model and the plugin implementation.

---

## Facilitator Plugin

### Plugin Registration

```python
# services/ai/agents/facilitator/plugins.py
class FacilitatorPlugin:
    """Tools for the Facilitator AI to interact with the idea workspace."""
```

---

### 1. send_chat_message

Posts an AI chat message to the idea's conversation.

**Function Definition:**

```json
{
  "name": "send_chat_message",
  "description": "Send a chat message to the idea's conversation. Use this to respond to users, ask clarifying questions, or post delegation messages. Supports board item references using [[Item Title]] syntax.",
  "parameters": {
    "type": "object",
    "properties": {
      "content": {
        "type": "string",
        "description": "The message text. Use [[Board Item Title]] to create clickable references to board items. Use natural conversational language."
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
| `idea_locked` | Idea is in a read-only state (accepted, dropped) | Return error. Facilitator should not have been triggered. |
| `rate_limited` | Chat is locked due to rate limit cap | Return error. Processing should not have started. |

**Implementation Notes:**
- The plugin publishes an `ai.chat_response.ready` event to the message broker.
- The gateway receives the event, persists the message via core service gRPC, and broadcasts via WebSocket.
- Board item references (`[[Title]]`) are validated against current board state. Invalid references are rendered as plain text.

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

Updates the idea's title. Only callable when `title_manually_edited` is false.

**Function Definition:**

```json
{
  "name": "update_title",
  "description": "Update the idea's title. Generate a short, concise title (under 60 characters) that reflects the current direction of the brainstorming. Call this when the idea is new (first title) or when the existing title no longer fits because the idea's scope has evolved. Do NOT call this if the system prompt indicates the title was manually edited.",
  "parameters": {
    "type": "object",
    "properties": {
      "title": {
        "type": "string",
        "maxLength": 60,
        "description": "The new title. Must be under 60 characters. Should be concise and descriptive of the idea's core topic."
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
  "description": "Delegate to the Context Agent to retrieve company-specific information from the knowledge base. Call this when the user's message relates to a topic listed in the facilitator bucket (company systems, domain terminology, org structure). IMPORTANT: Before calling this, you should first call send_chat_message with message_type 'delegation' to inform the user you are looking something up.",
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
        "description": "A precise description of what conversation detail to find. Be specific: 'What did Lisa say about the legal requirements for digital signatures?' is better than 'What was discussed earlier?'."
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
| `no_compressed_context` | `chat_context_summaries` does not exist for this idea (no compression has occurred) | Return error. All messages are already in the Facilitator's recent messages window — extension is unnecessary. |
| `history_unavailable` | Core gRPC `GetFullChatHistory` fails | Return error. Facilitator should respond: "I couldn't retrieve that detail from earlier." |

**Implementation Notes:**
- Publishes `ai.delegation.started` event (same event type as context agent delegation — the event payload includes `delegation_type: "context_extension"` to distinguish).
- The Context Extension Agent uses the Escalated model tier (larger context budget for full chat history).
- Timeout is 90s (1.5× `ai_processing_timeout`) to accommodate large chat histories.

---

### 6. request_board_changes

Outputs structured board modification instructions for the Board Agent.

**Function Definition:**

```json
{
  "name": "request_board_changes",
  "description": "Submit board modification instructions for the Board Agent to execute. Express SEMANTIC INTENT — describe what content to add, update, or reorganize and why. Reference board items by title. The Board Agent handles all spatial layout, grouping, and positioning. Only call this when the brainstorming has produced content that should be captured or restructured on the board.",
  "parameters": {
    "type": "object",
    "properties": {
      "instructions": {
        "type": "array",
        "description": "List of board modification instructions. Each describes a semantic change to the board.",
        "items": {
          "type": "object",
          "properties": {
            "intent": {
              "type": "string",
              "enum": ["add_topic", "update_topic", "remove_topic", "reorganize", "add_relationship", "update_relationship", "remove_relationship"],
              "description": "The type of board modification."
            },
            "description": {
              "type": "string",
              "description": "Natural language explanation of what to do and why. This helps the Board Agent make intelligent layout decisions."
            },
            "suggested_title": {
              "type": "string",
              "description": "Suggested title for new boxes or groups. Used with add_topic intent."
            },
            "suggested_content": {
              "type": "array",
              "items": { "type": "string" },
              "description": "Bullet points for box content. Used with add_topic intent."
            },
            "target": {
              "type": "string",
              "description": "Title of an existing board item to modify. Used with update_topic, remove_topic intents."
            },
            "updated_content": {
              "type": "array",
              "items": { "type": "string" },
              "description": "Updated bullet points. Used with update_topic intent. Replaces existing content."
            },
            "related_to": {
              "type": "array",
              "items": { "type": "string" },
              "description": "Titles of existing board items this new item is related to. Used with add_topic intent."
            },
            "suggested_group": {
              "type": "string",
              "description": "Name of the group this item should belong to. The Board Agent creates the group if it doesn't exist. Used with add_topic intent."
            },
            "items_affected": {
              "type": "array",
              "items": { "type": "string" },
              "description": "Titles of board items affected by reorganization. Used with reorganize intent."
            },
            "suggested_structure": {
              "type": "string",
              "description": "Description of the desired organizational structure. Used with reorganize intent."
            },
            "source": {
              "type": "string",
              "description": "Title of the source board item for a relationship. Used with add_relationship, update_relationship, remove_relationship intents."
            },
            "new_label": {
              "type": "string",
              "description": "Label for a connection. Used with add_relationship, update_relationship intents."
            }
          },
          "required": ["intent", "description"]
        },
        "minItems": 1
      }
    },
    "required": ["instructions"]
  }
}
```

**Return Schema:**

```json
{
  "type": "object",
  "properties": {
    "accepted": {
      "type": "boolean",
      "description": "Whether the instructions were accepted for processing"
    },
    "instruction_count": {
      "type": "integer",
      "description": "Number of instructions queued"
    }
  }
}
```

**Asynchronous Flow:**

Like delegation, this tool is **non-blocking**. The Board Agent processes instructions after the Facilitator's SK function calling loop completes. Board updates are broadcast to users via WebSocket as they are executed.

**Error Cases:**

| Error | Condition | Behavior |
|-------|-----------|----------|
| `idea_locked` | Idea brainstorming section is in read-only state | Return error. No board modifications allowed. |

**Implementation Notes:**
- Instructions are passed to the Board Agent via the pipeline orchestrator (not via message broker — this is an in-process handoff within the AI service).
- The Board Agent receives the instructions JSON + current board state and executes changes using its own tools.
- Each board mutation generates an `ai.board.updated` event.

---

## Board Agent Plugin

### Plugin Registration

```python
# services/ai/agents/board_agent/plugins.py
class BoardPlugin:
    """Tools for the Board Agent to modify the digital board."""
```

---

### 1. create_node

Creates a new board node (Box, Group, or Free Text).

**Function Definition:**

```json
{
  "name": "create_node",
  "description": "Create a new node on the board. Use 'box' for content cards (one topic per box, bullet-point body). Use 'group' for containers that organize related boxes. Use 'free_text' for standalone text on the canvas. Position the node thoughtfully — near related items, inside the correct group, avoiding overlaps with existing nodes.",
  "parameters": {
    "type": "object",
    "properties": {
      "node_type": {
        "type": "string",
        "enum": ["box", "group", "free_text"],
        "description": "The type of node to create."
      },
      "title": {
        "type": "string",
        "description": "Title for the node. Required for box and group. Not used for free_text.",
        "maxLength": 500
      },
      "body": {
        "type": "string",
        "description": "Body content. For box: bullet points (one per line, prefixed with '- '). For free_text: plain text. Not used for group.",
        "maxLength": 5000
      },
      "position_x": {
        "type": "number",
        "description": "X position on the canvas in pixels. 0 is the left edge."
      },
      "position_y": {
        "type": "number",
        "description": "Y position on the canvas in pixels. 0 is the top edge."
      },
      "width": {
        "type": "number",
        "description": "Width in pixels. Required for group nodes (to size the container). Optional for others.",
        "default": 250
      },
      "height": {
        "type": "number",
        "description": "Height in pixels. Required for group nodes. Optional for others.",
        "default": 150
      },
      "parent_id": {
        "type": "string",
        "format": "uuid",
        "description": "ID of the parent group node. Set this to place the new node inside a group. Null for top-level nodes."
      }
    },
    "required": ["node_type", "position_x", "position_y"]
  }
}
```

**Return Schema:**

```json
{
  "type": "object",
  "properties": {
    "node_id": {
      "type": "string",
      "format": "uuid",
      "description": "The ID of the created node"
    },
    "node_type": {
      "type": "string"
    },
    "position_x": {
      "type": "number"
    },
    "position_y": {
      "type": "number"
    }
  }
}
```

**Error Cases:**

| Error | Condition | Behavior |
|-------|-----------|----------|
| `invalid_parent` | parent_id does not exist or is not a group node | Return error with description. Node not created. |
| `missing_title` | node_type is box or group but title is empty/missing | Return error. Boxes and groups require titles. |

**Implementation Notes:**
- `created_by` is automatically set to `'ai'`.
- `ai_modified_indicator` is automatically set to `true`.
- The node is persisted to the `board_nodes` table via core service gRPC.
- An `ai.board.updated` event is published with the create mutation.

---

### 2. update_node

Updates an existing node's content or properties.

**Function Definition:**

```json
{
  "name": "update_node",
  "description": "Update the title or body content of an existing board node. Use this to refine existing content, add new bullet points, or correct information. Do NOT update locked nodes. When updating a box body, provide the COMPLETE new body (all bullet points), not just the additions.",
  "parameters": {
    "type": "object",
    "properties": {
      "node_id": {
        "type": "string",
        "format": "uuid",
        "description": "The ID of the node to update."
      },
      "title": {
        "type": "string",
        "description": "New title. Omit to keep existing title.",
        "maxLength": 500
      },
      "body": {
        "type": "string",
        "description": "New body content. Omit to keep existing body. For boxes: complete bullet-point list (replaces existing body entirely).",
        "maxLength": 5000
      }
    },
    "required": ["node_id"]
  }
}
```

**Return Schema:**

```json
{
  "type": "object",
  "properties": {
    "node_id": {
      "type": "string",
      "format": "uuid"
    },
    "updated_fields": {
      "type": "array",
      "items": { "type": "string" },
      "description": "List of fields that were updated (e.g., ['title', 'body'])"
    }
  }
}
```

**Error Cases:**

| Error | Condition | Behavior |
|-------|-----------|----------|
| `node_not_found` | node_id does not exist | Return error. |
| `node_locked` | Node's `is_locked` flag is true | Return error. Locked nodes cannot be modified by AI. |
| `no_changes` | Neither title nor body provided | Return error. At least one field must be updated. |

**Implementation Notes:**
- `ai_modified_indicator` is set to `true` on update.
- `updated_at` timestamp is refreshed.
- Publishes mutation in `ai.board.updated` event.

---

### 3. delete_node

Removes a node from the board.

**Function Definition:**

```json
{
  "name": "delete_node",
  "description": "Delete a node from the board. Use this to remove obsolete or duplicate items. When deleting a group, all child nodes are detached (moved to top-level), NOT deleted. Associated connections are automatically removed. Do NOT delete locked nodes.",
  "parameters": {
    "type": "object",
    "properties": {
      "node_id": {
        "type": "string",
        "format": "uuid",
        "description": "The ID of the node to delete."
      }
    },
    "required": ["node_id"]
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
    "detached_children": {
      "type": "array",
      "items": { "type": "string", "format": "uuid" },
      "description": "IDs of child nodes that were detached from the deleted group (empty if not a group)"
    }
  }
}
```

**Error Cases:**

| Error | Condition | Behavior |
|-------|-----------|----------|
| `node_not_found` | node_id does not exist | Return error. |
| `node_locked` | Node's `is_locked` flag is true | Return error. |

**Implementation Notes:**
- Group deletion sets `parent_id = NULL` on all children (ON DELETE SET NULL from DB schema).
- Connection deletion cascades (ON DELETE CASCADE from DB schema).
- Board Agent should consider repositioning detached children after deleting a group.

---

### 4. move_node

Changes a node's position on the canvas.

**Function Definition:**

```json
{
  "name": "move_node",
  "description": "Move a node to a new position on the canvas. Use this during reorganization to improve layout. When moving a node into or out of a group, also update its parent_id using the new_parent_id parameter. Moving a group moves all its children along with it.",
  "parameters": {
    "type": "object",
    "properties": {
      "node_id": {
        "type": "string",
        "format": "uuid",
        "description": "The ID of the node to move."
      },
      "position_x": {
        "type": "number",
        "description": "New X position in pixels."
      },
      "position_y": {
        "type": "number",
        "description": "New Y position in pixels."
      },
      "new_parent_id": {
        "type": "string",
        "format": "uuid",
        "description": "Set to move the node into a different group. Set to null to detach from current group. Omit to keep current parent."
      }
    },
    "required": ["node_id", "position_x", "position_y"]
  }
}
```

**Return Schema:**

```json
{
  "type": "object",
  "properties": {
    "node_id": {
      "type": "string",
      "format": "uuid"
    },
    "position_x": { "type": "number" },
    "position_y": { "type": "number" },
    "parent_changed": {
      "type": "boolean",
      "description": "Whether the node's parent group was changed"
    }
  }
}
```

**Error Cases:**

| Error | Condition | Behavior |
|-------|-----------|----------|
| `node_not_found` | node_id does not exist | Return error. |
| `node_locked` | Node is locked | Return error. |
| `invalid_parent` | new_parent_id is not a group node or does not exist | Return error. |

**Implementation Notes:**
- When moving a group, all children move with it (their relative positions to the group origin are preserved).
- `ai_modified_indicator` is set to `true`.
- Child position recalculation is handled by the plugin implementation, not by the model.

---

### 5. resize_group

Resizes a group container.

**Function Definition:**

```json
{
  "name": "resize_group",
  "description": "Resize a group container. Use this after adding or removing children to ensure the group properly contains all its items with appropriate padding (40px recommended on all sides).",
  "parameters": {
    "type": "object",
    "properties": {
      "node_id": {
        "type": "string",
        "format": "uuid",
        "description": "The ID of the group node to resize. Must be a node with node_type 'group'."
      },
      "width": {
        "type": "number",
        "description": "New width in pixels."
      },
      "height": {
        "type": "number",
        "description": "New height in pixels."
      }
    },
    "required": ["node_id", "width", "height"]
  }
}
```

**Return Schema:**

```json
{
  "type": "object",
  "properties": {
    "node_id": {
      "type": "string",
      "format": "uuid"
    },
    "width": { "type": "number" },
    "height": { "type": "number" }
  }
}
```

**Error Cases:**

| Error | Condition | Behavior |
|-------|-----------|----------|
| `node_not_found` | node_id does not exist | Return error. |
| `not_a_group` | Node is not of type 'group' | Return error. Only groups can be resized via this tool. |
| `node_locked` | Group is locked | Return error. |

---

### 6. create_connection

Creates an edge between two board nodes.

**Function Definition:**

```json
{
  "name": "create_connection",
  "description": "Create a connection (edge) between two board nodes to express a relationship. Use clear, descriptive labels: 'depends on', 'enables', 'conflicts with', 'part of', 'leads to', etc. Connections can be created between any node types.",
  "parameters": {
    "type": "object",
    "properties": {
      "source_node_id": {
        "type": "string",
        "format": "uuid",
        "description": "The ID of the source node (where the connection starts)."
      },
      "target_node_id": {
        "type": "string",
        "format": "uuid",
        "description": "The ID of the target node (where the connection points to)."
      },
      "label": {
        "type": "string",
        "description": "Descriptive label for the relationship. Should be short (2-4 words). Optional but recommended.",
        "maxLength": 500
      }
    },
    "required": ["source_node_id", "target_node_id"]
  }
}
```

**Return Schema:**

```json
{
  "type": "object",
  "properties": {
    "connection_id": {
      "type": "string",
      "format": "uuid",
      "description": "The ID of the created connection"
    }
  }
}
```

**Error Cases:**

| Error | Condition | Behavior |
|-------|-----------|----------|
| `node_not_found` | source or target node does not exist | Return error identifying which node is missing. |
| `self_connection` | source_node_id == target_node_id | Return error. Nodes cannot connect to themselves. |
| `duplicate_connection` | Connection between this source-target pair already exists | Return error. Use update_connection to change the label. |

**Implementation Notes:**
- Enforces the unique constraint `uq_board_connection` (source_node_id, target_node_id).
- Connections are directional (source → target).

---

### 7. update_connection

Updates a connection's label.

**Function Definition:**

```json
{
  "name": "update_connection",
  "description": "Update the label of an existing connection between two nodes. Use this to refine or correct relationship descriptions.",
  "parameters": {
    "type": "object",
    "properties": {
      "connection_id": {
        "type": "string",
        "format": "uuid",
        "description": "The ID of the connection to update."
      },
      "label": {
        "type": "string",
        "description": "New label for the connection. Set to empty string to remove the label.",
        "maxLength": 500
      }
    },
    "required": ["connection_id", "label"]
  }
}
```

**Return Schema:**

```json
{
  "type": "object",
  "properties": {
    "connection_id": {
      "type": "string",
      "format": "uuid"
    },
    "label": {
      "type": "string"
    }
  }
}
```

**Error Cases:**

| Error | Condition | Behavior |
|-------|-----------|----------|
| `connection_not_found` | connection_id does not exist | Return error. |

---

### 8. delete_connection

Removes a connection between two nodes.

**Function Definition:**

```json
{
  "name": "delete_connection",
  "description": "Delete a connection (edge) between two nodes. Use this when a relationship is no longer valid or was created in error.",
  "parameters": {
    "type": "object",
    "properties": {
      "connection_id": {
        "type": "string",
        "format": "uuid",
        "description": "The ID of the connection to delete."
      }
    },
    "required": ["connection_id"]
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
    }
  }
}
```

**Error Cases:**

| Error | Condition | Behavior |
|-------|-----------|----------|
| `connection_not_found` | connection_id does not exist | Return error. |

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
| `node_not_found` | The referenced node ID does not exist in the current board |
| `connection_not_found` | The referenced connection ID does not exist |
| `node_locked` | The target node is locked and cannot be modified |
| `invalid_parent` | The specified parent ID is not a valid group node |
| `idea_locked` | The idea is in a read-only state (accepted, dropped, or in_review for brainstorming section) |
| `rate_limited` | Chat input is locked due to rate limit cap |
| `context_bucket_empty` | The context agent bucket has no content for RAG retrieval |
| `no_compressed_context` | No chat compression has occurred — context extension is unnecessary |
| `history_unavailable` | Full chat history could not be retrieved from Core service |
| `validation_error` | Input parameters failed validation (details in error.details) |

---

## SK Plugin Implementation Pattern

All plugins follow the same implementation pattern using Semantic Kernel decorators:

```python
from semantic_kernel.functions import kernel_function
from pydantic import BaseModel, Field

class CreateNodeInput(BaseModel):
    """Input schema for create_node, validated by Pydantic."""
    node_type: str = Field(..., pattern="^(box|group|free_text)$")
    title: str | None = Field(None, max_length=500)
    body: str | None = Field(None, max_length=5000)
    position_x: float
    position_y: float
    width: float = 250
    height: float = 150
    parent_id: str | None = None

class CreateNodeOutput(BaseModel):
    """Return schema for create_node."""
    node_id: str
    node_type: str
    position_x: float
    position_y: float

class BoardPlugin:
    def __init__(self, idea_id: str, core_client: CoreGrpcClient):
        self.idea_id = idea_id
        self.core_client = core_client

    @kernel_function(
        name="create_node",
        description="Create a new node on the board..."
    )
    async def create_node(self, input: CreateNodeInput) -> CreateNodeOutput:
        # Validate locked state
        # Call core service via gRPC to persist
        # Publish ai.board.updated event
        # Return result
        ...
```

**Key patterns:**
- **Pydantic models** for input validation and output serialization.
- **gRPC calls** to the core service for all persistence operations.
- **Event publishing** for all mutations (consumed by gateway for WebSocket broadcast).
- **Error handling** catches gRPC errors and converts to the standard error response format.
- **Idea context** (idea_id, locked state) is injected at plugin initialization, not passed per call.

---

## Tool Execution Flow

### Facilitator — Multi-Turn Function Calling

The Facilitator uses SK's automatic function calling loop. In a single processing cycle, the model may call multiple tools across multiple turns:

```
Turn 1: Model decides to respond + create board items + update title
  → calls send_chat_message(content="...")
  → calls update_title(title="...")
  → calls request_board_changes(instructions=[...])

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

### Board Agent — Sequential Tool Execution

The Board Agent processes Facilitator instructions by calling tools sequentially:

```
Turn 1: Model reads instructions + board state
  → calls create_node(type="group", title="Pain Points", ...)

Turn 2: Model receives new group ID
  → calls create_node(type="box", title="Manual Invoice Approval", parent_id=<group_id>, ...)

Turn 3: Model receives new box ID
  → calls create_connection(source=<box_id>, target=<existing_box_id>, label="related")
  → calls resize_group(node_id=<group_id>, width=600, height=400)

Turn 4: Model receives results, all instructions executed
  → loop ends
```

**SK configuration:**
- `max_auto_invoke_attempts`: 10 (Board Agent may need many rounds for complex reorganizations)
- `function_choice_behavior`: auto

---

## Validation Rules Summary

| Tool | Key Validations |
|------|----------------|
| send_chat_message | content is non-empty; idea is not in read-only state |
| react_to_message | target message exists; target is a user message; no existing AI reaction on that message |
| update_title | title ≤ 60 chars; title_manually_edited is false |
| delegate_to_context_agent | query is non-empty; context agent bucket has content |
| delegate_to_context_extension | query is non-empty; compressed context exists for this idea; Core gRPC reachable |
| request_board_changes | at least 1 instruction; each instruction has intent + description |
| create_node | valid node_type; box/group have title; valid parent_id if provided |
| update_node | node exists; node not locked; at least one field to update |
| delete_node | node exists; node not locked |
| move_node | node exists; node not locked; valid new_parent_id if provided |
| resize_group | node exists; node is a group; node not locked |
| create_connection | both nodes exist; not a self-connection; no duplicate connection |
| update_connection | connection exists |
| delete_connection | connection exists |
