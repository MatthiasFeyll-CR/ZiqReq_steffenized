# Test Fixtures & Mocks

> **Status:** Definitive (revised)
> **Date:** 2026-03-05 (originally 2026-03-04)
> **Author:** Test Architect (Phase 4b)
> **Input:** `test-plan.md`, `test-matrix.md`, `docs/02-architecture/data-model.md`, `docs/03-ai/agent-architecture.md`
> **Revision:** Added MonitoringAlertConfigFactory, CollaborationFlow composite scenario, review timeline version links

This document defines all shared test data, factory functions, mock services, seed scripts, and determinism strategies. It complements the test plan's Shared Test Utilities section with concrete field-level specifications.

---

## 1. Backend Factory Functions

All factories use [factory_boy](https://factoryboy.readthedocs.io/) with Django model integration. Located in `services/core/tests/factories.py` (shared across core and gateway via Python path).

### 1.1 UserFactory

```
Location: services/core/tests/factories.py
```

| Field | Default Strategy | Notes |
|-------|-----------------|-------|
| `id` | `factory.LazyFunction(uuid4)` | Simulates Azure AD object ID |
| `email` | `factory.Sequence(lambda n: f"user{n}@commerz-real.test")` | Unique per instance |
| `first_name` | `"Test"` | |
| `last_name` | `factory.Sequence(lambda n: f"User{n}")` | |
| `display_name` | `factory.LazyAttribute(lambda o: f"{o.first_name} {o.last_name}")` | |
| `roles` | `["user"]` | Override: `["user", "reviewer"]`, `["user", "admin"]` |
| `email_notification_preferences` | `{}` | Empty = all enabled |
| `last_login_at` | `factory.LazyFunction(timezone.now)` | |

**Named variants (traits):**

| Trait | Overrides |
|-------|-----------|
| `reviewer` | `roles=["user", "reviewer"]` |
| `admin` | `roles=["user", "admin"]` |
| `admin_reviewer` | `roles=["user", "reviewer", "admin"]` |

---

### 1.2 IdeaFactory

```
Location: services/core/tests/factories.py
```

| Field | Default Strategy | Notes |
|-------|-----------------|-------|
| `id` | `factory.LazyFunction(uuid4)` | |
| `title` | `factory.Sequence(lambda n: f"Test Idea {n}")` | |
| `title_manually_edited` | `False` | |
| `state` | `"open"` | |
| `visibility` | `"private"` | |
| `agent_mode` | `"interactive"` | |
| `owner_id` | `factory.SubFactory(UserFactory)` | Auto-creates owner |
| `co_owner_id` | `None` | Set for merged idea tests |
| `share_link_token` | `None` | |
| `deleted_at` | `None` | Set for trash/soft-delete tests |

**Named variants (traits):**

| Trait | Overrides |
|-------|-----------|
| `in_review` | `state="in_review"` |
| `accepted` | `state="accepted"` |
| `dropped` | `state="dropped"` |
| `rejected` | `state="rejected"` |
| `collaborative` | `visibility="collaborating"` |
| `silent_mode` | `agent_mode="silent"` |
| `soft_deleted` | `deleted_at=timezone.now() - timedelta(days=5)` |
| `merged` | `co_owner_id=SubFactory(UserFactory), merged_from_idea_1_id=LazyFunction(uuid4), merged_from_idea_2_id=LazyFunction(uuid4)` |
| `shared` | `share_link_token=factory.LazyFunction(lambda: secrets.token_urlsafe(48))` |

---

### 1.3 IdeaCollaboratorFactory

```
Location: services/core/tests/factories.py
```

| Field | Default Strategy | Notes |
|-------|-----------------|-------|
| `idea` | `factory.SubFactory(IdeaFactory)` | |
| `user` | `factory.SubFactory(UserFactory)` | |
| `joined_at` | `factory.LazyFunction(timezone.now)` | |

---

### 1.4 ChatMessageFactory

```
Location: services/core/tests/factories.py
```

| Field | Default Strategy | Notes |
|-------|-----------------|-------|
| `id` | `factory.LazyFunction(uuid4)` | |
| `idea` | `factory.SubFactory(IdeaFactory)` | |
| `sender_type` | `"user"` | |
| `sender_id` | `factory.SubFactory(UserFactory)` | NULL for AI messages |
| `ai_agent` | `None` | Set for AI messages |
| `content` | `factory.Sequence(lambda n: f"Test message {n}")` | |
| `message_type` | `"regular"` | |

**Named variants (traits):**

| Trait | Overrides |
|-------|-----------|
| `ai_facilitator` | `sender_type="ai", sender_id=None, ai_agent="facilitator"` |
| `ai_context` | `sender_type="ai", sender_id=None, ai_agent="context_agent"` |
| `delegation` | `message_type="delegation"` |
| `with_mention` | `content="@ai Can you help with this?"` |

---

### 1.5 AiReactionFactory

```
Location: services/core/tests/factories.py
```

| Field | Default Strategy | Notes |
|-------|-----------------|-------|
| `message` | `factory.SubFactory(ChatMessageFactory)` | |
| `reaction_type` | `"thumbs_up"` | |

---

### 1.6 UserReactionFactory

```
Location: services/core/tests/factories.py
```

| Field | Default Strategy | Notes |
|-------|-----------------|-------|
| `message` | `factory.SubFactory(ChatMessageFactory)` | Must be a user message |
| `user` | `factory.SubFactory(UserFactory)` | Must differ from message sender |
| `reaction_type` | `"thumbs_up"` | |

---

### 1.7 BoardNodeFactory

```
Location: services/core/tests/factories.py
```

| Field | Default Strategy | Notes |
|-------|-----------------|-------|
| `id` | `factory.LazyFunction(uuid4)` | |
| `idea` | `factory.SubFactory(IdeaFactory)` | |
| `node_type` | `"box"` | |
| `title` | `factory.Sequence(lambda n: f"Node {n}")` | |
| `body` | `"- Bullet point 1\n- Bullet point 2"` | |
| `position_x` | `factory.Sequence(lambda n: float(n * 200))` | Spaced out |
| `position_y` | `factory.Sequence(lambda n: float(n * 150))` | |
| `width` | `None` | Set for groups |
| `height` | `None` | Set for groups |
| `parent_id` | `None` | Set for nested nodes |
| `is_locked` | `False` | |
| `created_by` | `"user"` | |
| `ai_modified_indicator` | `False` | |

**Named variants (traits):**

| Trait | Overrides |
|-------|-----------|
| `group` | `node_type="group", title="Group", body=None, width=400.0, height=300.0` |
| `free_text` | `node_type="free_text", title=None, body="Free text content"` |
| `ai_created` | `created_by="ai", ai_modified_indicator=True` |
| `locked` | `is_locked=True` |

---

### 1.8 BoardConnectionFactory

```
Location: services/core/tests/factories.py
```

| Field | Default Strategy | Notes |
|-------|-----------------|-------|
| `idea` | `factory.SubFactory(IdeaFactory)` | |
| `source_node` | `factory.SubFactory(BoardNodeFactory)` | |
| `target_node` | `factory.SubFactory(BoardNodeFactory)` | |
| `label` | `None` | |

---

### 1.9 BrdDraftFactory

```
Location: services/core/tests/factories.py
```

| Field | Default Strategy | Notes |
|-------|-----------------|-------|
| `idea` | `factory.SubFactory(IdeaFactory)` | One per idea (UNIQUE) |
| `section_title` | `"Test Idea Title"` | |
| `section_short_description` | `"A brief description of the idea."` | |
| `section_current_workflow` | `"Current process involves manual steps."` | |
| `section_affected_department` | `"IT Department"` | |
| `section_core_capabilities` | `"- Capability 1\n- Capability 2"` | |
| `section_success_criteria` | `"Reduced processing time by 50%."` | |
| `section_locks` | `{}` | |
| `allow_information_gaps` | `False` | |
| `readiness_evaluation` | `{}` | |

**Named variants (traits):**

| Trait | Overrides |
|-------|-----------|
| `with_locks` | `section_locks={"short_description": True, "core_capabilities": True}` |
| `with_gaps` | `allow_information_gaps=True` |
| `fully_ready` | `readiness_evaluation={"title": "ready", "short_description": "ready", "current_workflow": "ready", "affected_department": "ready", "core_capabilities": "ready", "success_criteria": "ready"}` |
| `partially_ready` | `readiness_evaluation={"title": "ready", "short_description": "ready", "current_workflow": "insufficient", "success_criteria": "insufficient"}` |
| `empty` | All section fields `None` |

---

### 1.10 BrdVersionFactory

```
Location: services/core/tests/factories.py
```

| Field | Default Strategy | Notes |
|-------|-----------------|-------|
| `idea` | `factory.SubFactory(IdeaFactory)` | |
| `version_number` | `factory.Sequence(lambda n: n + 1)` | |
| `section_title` | `"Frozen Title"` | |
| `section_short_description` | `"Frozen description."` | |
| `section_current_workflow` | `"Frozen workflow."` | |
| `section_affected_department` | `"IT Department"` | |
| `section_core_capabilities` | `"- Frozen capability"` | |
| `section_success_criteria` | `"Frozen criteria."` | |
| `pdf_file_path` | `None` | |

---

### 1.11 ReviewAssignmentFactory

```
Location: services/core/tests/factories.py
```

| Field | Default Strategy | Notes |
|-------|-----------------|-------|
| `idea` | `factory.SubFactory(IdeaFactory, state="in_review")` | |
| `reviewer` | `factory.SubFactory(UserFactory, roles=["user", "reviewer"])` | |
| `assigned_by` | `"submitter"` | |
| `unassigned_at` | `None` | Active assignment |

**Named variants (traits):**

| Trait | Overrides |
|-------|-----------|
| `self_assigned` | `assigned_by="self"` |
| `unassigned` | `unassigned_at=timezone.now()` |

---

### 1.12 ReviewTimelineEntryFactory

```
Location: services/core/tests/factories.py
```

| Field | Default Strategy | Notes |
|-------|-----------------|-------|
| `idea` | `factory.SubFactory(IdeaFactory)` | |
| `entry_type` | `"comment"` | |
| `author` | `factory.SubFactory(UserFactory)` | |
| `content` | `"Review comment text."` | |
| `parent_entry_id` | `None` | Set for replies |
| `old_state` | `None` | Set for state_change |
| `new_state` | `None` | Set for state_change |

**Named variants (traits):**

| Trait | Overrides |
|-------|-----------|
| `state_change` | `entry_type="state_change", content=None, old_state="open", new_state="in_review"` |
| `resubmission` | `entry_type="resubmission", content="Updated based on feedback", old_version_id=SubFactory(BrdVersionFactory), new_version_id=SubFactory(BrdVersionFactory)` |
| `reply` | `parent_entry_id=factory.SubFactory(ReviewTimelineEntryFactory)` |

---

### 1.13 CollaborationInvitationFactory

```
Location: services/core/tests/factories.py
```

| Field | Default Strategy | Notes |
|-------|-----------------|-------|
| `idea` | `factory.SubFactory(IdeaFactory)` | |
| `inviter` | `factory.SubFactory(UserFactory)` | Must be idea owner |
| `invitee` | `factory.SubFactory(UserFactory)` | |
| `status` | `"pending"` | |
| `responded_at` | `None` | |

**Named variants (traits):**

| Trait | Overrides |
|-------|-----------|
| `accepted` | `status="accepted", responded_at=timezone.now()` |
| `declined` | `status="declined", responded_at=timezone.now()` |
| `revoked` | `status="revoked", responded_at=timezone.now()` |

---

### 1.14 NotificationFactory

```
Location: services/gateway/tests/factories.py
```

| Field | Default Strategy | Notes |
|-------|-----------------|-------|
| `user` | `factory.SubFactory(UserFactory)` | Recipient |
| `event_type` | `"idea.submitted"` | |
| `title` | `"New idea submitted"` | |
| `body` | `"Your idea has been submitted for review."` | |
| `reference_id` | `factory.LazyFunction(uuid4)` | Related entity ID |
| `reference_type` | `"idea"` | |
| `is_read` | `False` | |
| `action_taken` | `False` | |

**Named variants (traits):**

| Trait | Overrides |
|-------|-----------|
| `read` | `is_read=True` |
| `actioned` | `is_read=True, action_taken=True` |
| `collaboration_invite` | `event_type="collaboration.invited", title="Collaboration invitation", reference_type="invitation"` |
| `merge_request` | `event_type="merge.requested", title="Merge request", reference_type="merge_request"` |
| `review_comment` | `event_type="review.comment_added", title="New review comment"` |

---

### 1.15 MergeRequestFactory

```
Location: services/core/tests/factories.py
```

| Field | Default Strategy | Notes |
|-------|-----------------|-------|
| `requesting_idea` | `factory.SubFactory(IdeaFactory)` | |
| `target_idea` | `factory.SubFactory(IdeaFactory)` | |
| `merge_type` | `"merge"` | |
| `requested_by` | `factory.SubFactory(UserFactory)` | |
| `status` | `"pending"` | |
| `requesting_owner_consent` | `"accepted"` | Requester implicitly consents |
| `target_owner_consent` | `"pending"` | |
| `reviewer_consent` | `"not_required"` | Set for append type |
| `resulting_idea_id` | `None` | Set on merge completion |

**Named variants (traits):**

| Trait | Overrides |
|-------|-----------|
| `append` | `merge_type="append", reviewer_consent="pending", target_idea=SubFactory(IdeaFactory, state="in_review")` |
| `fully_consented` | `target_owner_consent="accepted"` |
| `declined` | `status="declined"` |
| `completed` | `status="accepted", resulting_idea_id=LazyFunction(uuid4)` |

---

### 1.16 AdminParameterFactory

```
Location: services/core/tests/factories.py
```

| Field | Default Strategy | Notes |
|-------|-----------------|-------|
| `key` | `factory.Sequence(lambda n: f"test_param_{n}")` | |
| `value` | `"10"` | |
| `default_value` | `"10"` | |
| `description` | `"Test parameter"` | |
| `data_type` | `"integer"` | |
| `category` | `"Application"` | |

---

### 1.17 MonitoringAlertConfigFactory

```
Location: services/gateway/tests/factories.py
```

| Field | Default Strategy | Notes |
|-------|-----------------|-------|
| `user` | `factory.SubFactory(UserFactory, roles=["user", "admin"])` | Must be admin |
| `is_active` | `True` | |

---

### 1.18 IdeaKeywordsFactory

```
Location: services/core/tests/factories.py
```

| Field | Default Strategy | Notes |
|-------|-----------------|-------|
| `idea` | `factory.SubFactory(IdeaFactory)` | One per idea |
| `keywords` | `["innovation", "automation", "efficiency"]` | |

---

## 2. AI Service Factory Functions

Located in `services/ai/tests/factories.py`.

### 2.1 ChatContextSummaryFactory

| Field | Default Strategy | Notes |
|-------|-----------------|-------|
| `idea_id` | `factory.LazyFunction(uuid4)` | UUID ref (no FK in AI service) |
| `summary_text` | `"The user discussed process optimization for the IT department."` | |
| `messages_covered_up_to_id` | `factory.LazyFunction(uuid4)` | |
| `compression_iteration` | `1` | |
| `context_window_usage_at_compression` | `0.65` | |

### 2.2 ContextChunkFactory

| Field | Default Strategy | Notes |
|-------|-----------------|-------|
| `bucket_id` | `factory.LazyFunction(uuid4)` | |
| `chunk_index` | `factory.Sequence(lambda n: n)` | |
| `chunk_text` | `"Company context chunk about existing applications."` | |
| `token_count` | `150` | |
| `embedding` | `factory.LazyFunction(lambda: [0.01] * 1536)` | Zero-ish vector |
| `source_section` | `"existing_applications"` | |

### 2.3 IdeaEmbeddingFactory

| Field | Default Strategy | Notes |
|-------|-----------------|-------|
| `idea_id` | `factory.LazyFunction(uuid4)` | |
| `embedding` | `factory.LazyFunction(lambda: [0.01] * 1536)` | |
| `source_text_hash` | `factory.LazyFunction(lambda: hashlib.sha256(b"test").hexdigest())` | |

---

## 3. Frontend Fixture Builders

All frontend fixtures are TypeScript factory functions returning typed objects. Each builder accepts `Partial<T>` overrides.

### 3.1 buildIdeaFixture

```
Location: frontend/src/test/fixtures/idea.ts
```

| Field | Default | Notes |
|-------|---------|-------|
| `id` | `crypto.randomUUID()` | |
| `title` | `"Test Idea"` | |
| `titleManuallyEdited` | `false` | |
| `state` | `"open"` | |
| `visibility` | `"private"` | |
| `agentMode` | `"interactive"` | |
| `ownerId` | `crypto.randomUUID()` | |
| `coOwnerId` | `null` | |
| `shareLinkToken` | `null` | |
| `deletedAt` | `null` | |
| `createdAt` | `new Date().toISOString()` | |
| `updatedAt` | `new Date().toISOString()` | |

**Preset builders:**

| Function | Description |
|----------|-------------|
| `buildOpenIdea(overrides?)` | Default open idea |
| `buildInReviewIdea(overrides?)` | `state: "in_review"` |
| `buildAcceptedIdea(overrides?)` | `state: "accepted"` |
| `buildMergedIdea(overrides?)` | With `coOwnerId`, `mergedFromIdea1Id`, `mergedFromIdea2Id` |
| `buildDeletedIdea(overrides?)` | With `deletedAt` set |

---

### 3.2 buildChatMessageFixture

```
Location: frontend/src/test/fixtures/chat.ts
```

| Field | Default | Notes |
|-------|---------|-------|
| `id` | `crypto.randomUUID()` | |
| `ideaId` | `crypto.randomUUID()` | |
| `senderType` | `"user"` | |
| `senderId` | `crypto.randomUUID()` | |
| `aiAgent` | `null` | |
| `content` | `"Test message"` | |
| `messageType` | `"regular"` | |
| `createdAt` | `new Date().toISOString()` | |

**Preset builders:**

| Function | Description |
|----------|-------------|
| `buildUserMessage(overrides?)` | Default user message |
| `buildAiMessage(overrides?)` | `senderType: "ai", senderId: null, aiAgent: "facilitator"` |
| `buildDelegationMessage(overrides?)` | `messageType: "delegation"` |

---

### 3.3 buildBoardNodeFixture

```
Location: frontend/src/test/fixtures/board.ts
```

| Field | Default | Notes |
|-------|---------|-------|
| `id` | `crypto.randomUUID()` | |
| `ideaId` | `crypto.randomUUID()` | |
| `nodeType` | `"box"` | |
| `title` | `"Test Node"` | |
| `body` | `"- Point 1\n- Point 2"` | |
| `positionX` | `0` | |
| `positionY` | `0` | |
| `width` | `null` | |
| `height` | `null` | |
| `parentId` | `null` | |
| `isLocked` | `false` | |
| `createdBy` | `"user"` | |
| `aiModifiedIndicator` | `false` | |

**Preset builders:**

| Function | Description |
|----------|-------------|
| `buildBoxNode(overrides?)` | Default box |
| `buildGroupNode(overrides?)` | `nodeType: "group", width: 400, height: 300, body: null` |
| `buildFreeTextNode(overrides?)` | `nodeType: "free_text", title: null` |
| `buildAiNode(overrides?)` | `createdBy: "ai", aiModifiedIndicator: true` |

---

### 3.4 buildBrdDraftFixture

```
Location: frontend/src/test/fixtures/brd.ts
```

| Field | Default | Notes |
|-------|---------|-------|
| `id` | `crypto.randomUUID()` | |
| `ideaId` | `crypto.randomUUID()` | |
| `sectionTitle` | `"Draft Title"` | |
| `sectionShortDescription` | `"A short description."` | |
| `sectionCurrentWorkflow` | `"Current workflow description."` | |
| `sectionAffectedDepartment` | `"IT"` | |
| `sectionCoreCapabilities` | `"- Cap 1\n- Cap 2"` | |
| `sectionSuccessCriteria` | `"Success criteria here."` | |
| `sectionLocks` | `{}` | |
| `allowInformationGaps` | `false` | |
| `readinessEvaluation` | `{}` | |

**Preset builders:**

| Function | Description |
|----------|-------------|
| `buildEmptyDraft(overrides?)` | All sections `null` |
| `buildFullDraft(overrides?)` | All sections filled |
| `buildLockedDraft(overrides?)` | `sectionLocks` with 2 locked sections |
| `buildReadyDraft(overrides?)` | All readiness statuses `"ready"` |

---

### 3.5 buildNotificationFixture

```
Location: frontend/src/test/fixtures/notification.ts
```

| Field | Default | Notes |
|-------|---------|-------|
| `id` | `crypto.randomUUID()` | |
| `userId` | `crypto.randomUUID()` | |
| `eventType` | `"idea.submitted"` | |
| `title` | `"Notification title"` | |
| `body` | `"Notification body"` | |
| `referenceId` | `crypto.randomUUID()` | |
| `referenceType` | `"idea"` | |
| `isRead` | `false` | |
| `actionTaken` | `false` | |
| `createdAt` | `new Date().toISOString()` | |

---

### 3.6 buildMergeRequestFixture

```
Location: frontend/src/test/fixtures/merge.ts
```

| Field | Default | Notes |
|-------|---------|-------|
| `id` | `crypto.randomUUID()` | |
| `requestingIdeaId` | `crypto.randomUUID()` | |
| `targetIdeaId` | `crypto.randomUUID()` | |
| `mergeType` | `"merge"` | |
| `requestedBy` | `crypto.randomUUID()` | |
| `status` | `"pending"` | |
| `requestingOwnerConsent` | `"accepted"` | |
| `targetOwnerConsent` | `"pending"` | |
| `reviewerConsent` | `"not_required"` | |
| `resultingIdeaId` | `null` | |

---

### 3.7 buildReviewAssignmentFixture

```
Location: frontend/src/test/fixtures/review.ts
```

| Field | Default | Notes |
|-------|---------|-------|
| `id` | `crypto.randomUUID()` | |
| `ideaId` | `crypto.randomUUID()` | |
| `reviewerId` | `crypto.randomUUID()` | |
| `assignedBy` | `"submitter"` | |
| `assignedAt` | `new Date().toISOString()` | |
| `unassignedAt` | `null` | |

---

## 4. Mock Services

### 4.1 MockAzureOpenAI

```
Location: services/ai/tests/helpers/mock_openai.py
```

| Aspect | Detail |
|--------|--------|
| **What it replaces** | Azure OpenAI API (`AsyncAzureOpenAI` client) |
| **Mock strategy** | Patched at `semantic_kernel.connectors.ai.open_ai` level. Returns pre-built `ChatCompletion` objects keyed by `(agent_name, scenario)`. |
| **Response registry** | Dictionary mapping `(agent_name, scenario_key)` → `ChatCompletion` fixture. Tests register expected responses before agent invocation. |
| **Function calling support** | For Facilitator/Board Agent: fixture responses include `tool_calls` with function name + JSON arguments. Mock tracks multi-round function calling loops (up to 3 for Facilitator, 10 for Board Agent). |
| **Token tracking** | Each fixture response includes `usage.prompt_tokens` and `usage.completion_tokens` for budget tests. |
| **Failure simulation** | `raise_on_call(n)` — raises `openai.APIError` on the Nth call to test retry logic. |
| **Timeout simulation** | `delay_response(seconds)` — adds async sleep before returning, for timeout tests. |

---

### 4.2 MockGrpcClient

```
Location: services/gateway/tests/helpers/grpc_mock.py
```

| Aspect | Detail |
|--------|--------|
| **What it replaces** | gRPC client stubs for gateway → core and gateway → AI communication |
| **Mock strategy** | `unittest.mock.AsyncMock` wrapping each gRPC stub method. Returns pre-built protobuf response objects. |
| **Configuration** | `configure_response(method_name, response)` — sets the return value for a specific RPC. `configure_error(method_name, grpc.StatusCode, message)` — raises gRPC error on call. |
| **Call tracking** | `assert_called(method_name, request_matcher)` — verifies the RPC was called with expected request fields. `call_count(method_name)` — returns number of calls. |
| **Services mocked** | `IdeaService`, `ChatService`, `BoardService`, `BrdService`, `ReviewService`, `UserService`, `AiService` |

---

### 4.3 MockBrokerPublisher

```
Location: services/core/tests/helpers/broker_mock.py
```

| Aspect | Detail |
|--------|--------|
| **What it replaces** | RabbitMQ publisher (pika-based or Celery-based event publishing) |
| **Mock strategy** | In-memory list that captures all published events. Replaces the real publisher via dependency injection or `unittest.mock.patch`. |
| **API** | `published_events` — list of `(routing_key, payload)` tuples. `assert_event_published(routing_key, payload_matcher)` — verifies event was published. `clear()` — resets captured events between tests. |
| **Event types captured** | `chat.message.created`, `ai.processing.started`, `ai.processing.completed`, `ai.board.updated`, `board.node.updated`, `notification.created`, `idea.state.changed`, `merge.requested`, `merge.completed` |

---

### 4.4 AuthenticatedAPIClient

```
Location: services/gateway/tests/helpers/api_client.py
```

| Aspect | Detail |
|--------|--------|
| **What it replaces** | Azure AD MSAL token validation middleware |
| **Mock strategy** | Extends DRF `APIClient`. Injects a mock user (from `UserFactory`) into `request.user` by patching the authentication backend. Bypasses MSAL token validation entirely. |
| **API** | `AuthenticatedAPIClient(user=UserFactory())` — creates client authenticated as specific user. `as_user(user)` — switches authenticated user mid-test. `as_anonymous()` — removes authentication (for 401 tests). |
| **Role testing** | Create client with `UserFactory(roles=["user", "reviewer"])` to test role-based access. |

---

### 4.5 MockWebSocketConsumer (Backend)

```
Location: services/gateway/tests/helpers/ws_mock.py
```

| Aspect | Detail |
|--------|--------|
| **What it replaces** | Django Channels WebSocket consumer test setup |
| **Mock strategy** | Uses `channels.testing.WebsocketCommunicator` with patched authentication. |
| **API** | `create_ws_communicator(user, idea_id)` — returns a connected `WebsocketCommunicator` subscribed to the idea's channel group. `send_event(communicator, event_type, payload)` — simulates server-side event. `receive_json(communicator)` — reads next message from client. |

---

### 4.6 createMockWebSocket (Frontend)

```
Location: frontend/src/test/helpers/websocket.ts
```

| Aspect | Detail |
|--------|--------|
| **What it replaces** | Browser WebSocket connection to gateway |
| **Mock strategy** | Mock object implementing the WebSocket interface. Tracks `send()` calls and allows programmatic server event emission. |
| **API** | `createMockWebSocket()` — returns `{ ws, emitServerEvent, getSentMessages, close }`. `emitServerEvent(type, payload)` — triggers `onmessage` with a server event. `getSentMessages()` — returns all `send()` calls for assertion. |

---

### 4.7 AI Mock Mode Fixture Responses

```
Location: services/ai/tests/fixtures/
```

When `AI_MOCK_MODE=True` (E2E tests), the AI service returns deterministic responses instead of calling Azure OpenAI. These fixture files define those responses:

| File | Agent | Scenarios |
|------|-------|-----------|
| `facilitator.py` | Facilitator | `new_idea` (greeting + initial question), `ongoing_chat` (follow-up with reaction + board instruction), `silent_mode` (no action), `delegation` (delegates to Context Agent), `title_update` (suggests title) |
| `board_agent.py` | Board Agent | `create_nodes` (3 boxes + 1 group), `update_nodes` (modify titles), `connect_nodes` (2 connections), `reorganize` (move + reparent) |
| `summarizing_ai.py` | Summarizing AI | `full_brd` (all 6 sections), `selective_brd` (respects locks), `gaps_mode` (includes /TODO markers), `insufficient` (some sections "insufficient") |
| `keyword_agent.py` | Keyword Agent | `standard` (10 keywords), `few_messages` (3 keywords), `max_keywords` (20 keywords) |
| `deep_comparison.py` | Deep Comparison | `similar` (confirms similarity), `not_similar` (denies similarity) |
| `context_agent.py` | Context Agent | `found_context` (returns RAG results), `no_context` (no relevant context found) |
| `context_compression.py` | Context Compression | `standard` (compressed summary) |
| `merge_synthesizer.py` | Merge Synthesizer | `standard` (synthesized context from two ideas) |

---

## 5. Composite Fixture Scenarios

Pre-built scenarios that combine multiple factories to create realistic test states. Located in `services/core/tests/scenarios.py`.

### 5.1 IdeaWithFullState

Creates a complete idea with chat history, board, BRD draft, and collaborators.

| Entity | Count | Configuration |
|--------|-------|---------------|
| User (owner) | 1 | `UserFactory()` |
| Idea | 1 | `IdeaFactory(owner=owner)` |
| Collaborators | 2 | `IdeaCollaboratorFactory(idea=idea)` |
| Chat messages (user) | 5 | `ChatMessageFactory(idea=idea, sender_id=owner)` |
| Chat messages (AI) | 3 | `ChatMessageFactory.ai_facilitator(idea=idea)` |
| AI reactions | 2 | `AiReactionFactory(message=user_msgs[0])` |
| Board nodes (boxes) | 4 | `BoardNodeFactory(idea=idea)` |
| Board nodes (group) | 1 | `BoardNodeFactory.group(idea=idea)` |
| Board connections | 3 | `BoardConnectionFactory(idea=idea)` |
| BRD draft | 1 | `BrdDraftFactory(idea=idea)` |
| Keywords | 1 | `IdeaKeywordsFactory(idea=idea)` |

### 5.2 IdeaInReview

Creates an idea that has been submitted for review with reviewers assigned.

| Entity | Count | Configuration |
|--------|-------|---------------|
| User (owner) | 1 | `UserFactory()` |
| Users (reviewers) | 2 | `UserFactory.reviewer()` |
| Idea | 1 | `IdeaFactory(owner=owner, state="in_review")` |
| BRD version | 1 | `BrdVersionFactory(idea=idea, version_number=1)` |
| Review assignments | 2 | `ReviewAssignmentFactory(idea=idea, reviewer=reviewer)` |
| Timeline entry | 1 | `ReviewTimelineEntryFactory.state_change(idea=idea, old_state="open", new_state="in_review")` |

### 5.3 MergeCandidatePair

Creates two ideas with overlapping keywords for merge testing.

| Entity | Count | Configuration |
|--------|-------|---------------|
| Users | 2 | `UserFactory()` each |
| Ideas | 2 | `IdeaFactory()` each with different owners |
| Keywords | 2 | Overlapping keywords (8+ shared) |
| Merge request | 1 | `MergeRequestFactory(requesting_idea=idea1, target_idea=idea2)` |

### 5.4 CollaborationFlow

Creates a complete collaboration setup with invitation accepted, both users active.

| Entity | Count | Configuration |
|--------|-------|---------------|
| User (owner) | 1 | `UserFactory()` |
| User (collaborator) | 1 | `UserFactory()` |
| Idea | 1 | `IdeaFactory(owner=owner, visibility="collaborating")` |
| Invitation | 1 | `CollaborationInvitationFactory.accepted(idea=idea, inviter=owner, invitee=collaborator)` |
| Collaborator record | 1 | `IdeaCollaboratorFactory(idea=idea, user=collaborator)` |
| Notifications | 2 | `NotificationFactory.collaboration_invite(user=collaborator)`, `NotificationFactory(event_type="collaboration.joined", user=owner)` |

---

### 5.5 AdminWithParameters

Creates an admin user with all default admin parameters seeded.

| Entity | Count | Configuration |
|--------|-------|---------------|
| User (admin) | 1 | `UserFactory.admin()` |
| Admin parameters | 13+ | All seed data parameters from data model |

---

## 6. Test Database Strategy

### 6.1 Per-Layer Strategy

| Layer | Database | Strategy | Speed |
|-------|----------|----------|-------|
| Backend unit | None | All DB access mocked via `unittest.mock.patch` | < 50ms |
| Backend integration | Django test DB | `TestCase` — transaction rollback per test | < 500ms |
| gRPC contract | Django test DB | Same as integration | < 200ms |
| WebSocket | Django test DB | `TransactionTestCase` (Channels requires committed transactions) | < 500ms |
| E2E | `ziqreq_test` DB | Docker Compose test profile, seed before suite | < 15s per test |

### 6.2 Test Database Configuration

```python
# services/core/settings/test.py (and gateway, ai)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "ziqreq_test",
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
        "USER": os.environ.get("DB_USER", "ziqreq"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "ziqreq_test"),
        "TEST": {"NAME": "ziqreq_test"},
    }
}

# Faster password hashing in tests
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Synchronous Celery for integration tests
CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES = True

# Disable rate limiting
REST_FRAMEWORK = {
    ...
    "DEFAULT_THROTTLE_CLASSES": [],
}
```

### 6.3 pgvector in Tests

The test database requires the pgvector extension for AI service tables (`context_chunks`, `idea_embeddings`). The Docker Compose test profile uses `pgvector/pgvector:pg16` image. For CI, the PostgreSQL service container includes pgvector pre-installed.

---

## 7. E2E Seed Data

Seed script: `e2e/scripts/seed-db.ts` (called by Playwright `globalSetup`).

| Entity | Data | Purpose |
|--------|------|---------|
| Users | 4 dev users matching auth bypass mode (F-7.1): Dev User 1 (user), Dev User 2 (user), Dev User 3 (user+reviewer), Dev User 4 (user+admin) | Consistent auth for E2E |
| Admin parameters | All 13+ seed parameters with defaults | App configuration |
| Facilitator context bucket | Single empty row | Singleton initialization |
| Context agent bucket | Single empty row | Singleton initialization |
| Ideas (user 1) | 3 ideas: 1 open with chat+board, 1 in_review with BRD, 1 accepted | Landing page tests |
| Ideas (user 2) | 1 idea with collaboration invitation to user 1 | Collaboration tests |
| Review assignments | User 3 assigned to review user 1's in_review idea | Review flow tests |
| Notifications | 5 mixed notifications for user 1 (2 unread, 3 read) | Notification bell tests |
| Merge request | Pending merge between user 1's open idea and user 2's open idea | Merge flow tests |

---

## 8. Determinism Helpers

### 8.1 Timestamps

| Context | Strategy | Implementation |
|---------|----------|----------------|
| Backend tests | `freezegun` library | `@freeze_time("2026-01-15T10:00:00Z")` decorator or `with freeze_time(...)` context manager |
| Frontend tests | Vitest fake timers | `vi.useFakeTimers(); vi.setSystemTime(new Date("2026-01-15T10:00:00Z"))` in `beforeEach` |
| E2E tests | No time freezing | Assertions use relative comparisons ("within last 5 minutes") not exact timestamps |

### 8.2 UUIDs

| Context | Strategy | Implementation |
|---------|----------|----------------|
| Backend tests | Factories generate real UUIDs | `factory.LazyFunction(uuid4)` — unique per instance, no collisions |
| Frontend tests | `crypto.randomUUID()` | Real UUIDs — no mocking needed |
| Deterministic IDs (when needed) | Named UUID fixtures | `TEST_USER_ID = UUID("00000000-0000-0000-0000-000000000001")` for cross-reference assertions |

### 8.3 External Service Calls

| Service | Strategy | Notes |
|---------|----------|-------|
| Azure OpenAI | `MockAzureOpenAI` (§4.1) | Never calls real API in any test layer |
| Azure AD / MSAL | `AuthenticatedAPIClient` (§4.4) + `mockAuthUser` (frontend) | Token validation bypassed |
| RabbitMQ | `MockBrokerPublisher` (§4.3) | Events captured in memory |
| gRPC (cross-service) | `MockGrpcClient` (§4.2) | Stub responses pre-configured |
| Email (notification service) | `django.core.mail.outbox` | Django's built-in test email backend |
| PDF generation | Mock WeasyPrint output | Returns a pre-built PDF bytes fixture |

### 8.4 Debounce & Async Timing

| Context | Strategy | Implementation |
|---------|----------|----------------|
| AI debounce timer (3s) | Freeze or advance time | Backend: `freezegun` advance. Frontend: `vi.advanceTimersByTime(3000)` |
| WebSocket reconnection backoff | Mock timer | Override reconnection delay to 0ms in test config |
| Celery tasks | Synchronous execution | `CELERY_ALWAYS_EAGER=True` — tasks execute inline |

---

## 9. Test Helper Functions

### 9.1 Frontend Helpers

| Helper | Location | Purpose |
|--------|----------|---------|
| `renderWithProviders(ui, options?)` | `frontend/src/test/helpers/render.tsx` | Wraps component in Redux store, QueryClient, Router, Theme (MUI), i18n provider. Accepts `initialState`, `route`, `user` overrides. |
| `createTestStore(initialState?)` | `frontend/src/test/helpers/store.ts` | Creates Redux store with optional pre-loaded state. Useful for testing slices in isolation. |
| `mockAuthUser(overrides?)` | `frontend/src/test/helpers/auth.ts` | Returns mock MSAL account info + token. Configurable: `roles`, `userId`, `email`, `displayName`. |
| `waitForQuerySettled(queryClient)` | `frontend/src/test/helpers/query.ts` | Awaits until all TanStack Query operations complete. Prevents "act()" warnings in async tests. |
| `createMockWebSocket()` | `frontend/src/test/helpers/websocket.ts` | See §4.6. |

### 9.2 Backend Helpers

| Helper | Location | Purpose |
|--------|----------|---------|
| `assert_event_published(mock_broker, routing_key, **matchers)` | `services/core/tests/helpers/assertions.py` | Asserts a specific event was published to the broker with matching payload fields. |
| `assert_grpc_called(mock_client, method, **request_matchers)` | `services/gateway/tests/helpers/assertions.py` | Asserts a gRPC method was called with expected request fields. |
| `assert_ws_message_sent(communicator, event_type, **payload_matchers)` | `services/gateway/tests/helpers/assertions.py` | Reads next WebSocket message and asserts type + payload. |
| `create_idea_with_state(state, **overrides)` | `services/core/tests/helpers/shortcuts.py` | Shortcut to create an idea in a specific lifecycle state with all required related objects (BRD version for in_review, review assignments, etc.). |

### 9.3 AI Service Helpers

| Helper | Location | Purpose |
|--------|----------|---------|
| `AgentTestHarness(agent_class, scenario)` | `services/ai/tests/helpers/agent_harness.py` | Base class for agent tests. Sets up Semantic Kernel, registers `MockAzureOpenAI`, provides `invoke()` and `assert_output_valid()`. |
| `assert_within_token_budget(result, max_tokens)` | `services/ai/tests/helpers/assertions.py` | Validates that agent response stayed within token budget. |
| `assert_no_fabrication(result, allowed_sources)` | `services/ai/tests/helpers/assertions.py` | Checks agent output doesn't reference entities not in the allowed source list. |
| `assert_guardrail_triggered(result, guardrail_name)` | `services/ai/tests/helpers/assertions.py` | Verifies a specific guardrail was activated (e.g., max iterations, content filter). |

---

## 10. Fixture File Summary

| Location | Files | Purpose |
|----------|-------|---------|
| `services/core/tests/factories.py` | 1 | All core entity factories (User through MergeRequest, 17 factories) |
| `services/core/tests/scenarios.py` | 1 | Composite fixture scenarios (5 scenarios) |
| `services/core/tests/helpers/` | `broker_mock.py`, `assertions.py`, `shortcuts.py` | Backend test helpers |
| `services/gateway/tests/factories.py` | 1 | Notification factory + MonitoringAlertConfig factory |
| `services/gateway/tests/helpers/` | `grpc_mock.py`, `api_client.py`, `ws_mock.py`, `assertions.py` | Gateway test helpers |
| `services/ai/tests/factories.py` | 1 | AI entity factories |
| `services/ai/tests/helpers/` | `mock_openai.py`, `agent_harness.py`, `assertions.py` | AI test helpers |
| `services/ai/tests/fixtures/` | 8 files | Per-agent fixture responses |
| `frontend/src/test/fixtures/` | `idea.ts`, `chat.ts`, `board.ts`, `brd.ts`, `notification.ts`, `merge.ts`, `review.ts` | Frontend fixture builders |
| `frontend/src/test/helpers/` | `render.tsx`, `store.ts`, `auth.ts`, `websocket.ts`, `query.ts` | Frontend test helpers |
| `e2e/scripts/seed-db.ts` | 1 | E2E database seeding |
