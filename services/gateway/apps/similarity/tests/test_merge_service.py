"""Tests for Merged Idea Creation — US-010 (T-5.5.03, T-5.5.06).

Tests the execute_merge function that:
- Creates a new merged idea with co-ownership
- Inserts synthesis message as first AI chat message
- Processes board instructions
- Transfers collaborators (deduplicated, excluding owners)
- Updates original ideas with closed_by_merge_id
- Updates merge_request with resulting_idea_id
- Publishes merge.complete event
- Runs atomically
"""

import uuid
from unittest.mock import patch

from django.test import TestCase

from apps.board.models import BoardNode
from apps.ideas.models import ChatMessage, Idea, IdeaCollaborator
from apps.similarity.models import MergeRequest

USER_A_ID = uuid.UUID("00000000-0000-0000-0000-000000001001")
USER_B_ID = uuid.UUID("00000000-0000-0000-0000-000000001002")
COLLAB_1_ID = uuid.UUID("00000000-0000-0000-0000-000000001003")
COLLAB_2_ID = uuid.UUID("00000000-0000-0000-0000-000000001004")
COLLAB_3_ID = uuid.UUID("00000000-0000-0000-0000-000000001005")

SYNTHESIS_MESSAGE = (
    "This merged idea combines the AI-powered image recognition system "
    "proposed by Owner A with the speech-to-text processing pipeline "
    "proposed by Owner B. Both ideas share a common foundation in neural "
    "network architectures and real-time processing requirements."
)

BOARD_INSTRUCTIONS = [
    {
        "intent": "create_node",
        "node_type": "group",
        "suggested_title": "Shared Foundation",
        "suggested_content": "Neural network architectures",
    },
    {
        "intent": "create_node",
        "node_type": "box",
        "suggested_title": "Image Recognition",
        "suggested_content": "Computer vision pipeline from Idea A",
    },
    {
        "intent": "create_node",
        "node_type": "box",
        "suggested_title": "Speech Processing",
        "suggested_content": "Audio processing pipeline from Idea B",
    },
]


@patch("apps.similarity.merge_service._publish_merge_complete")
class TestExecuteMerge(TestCase):
    """T-5.5.03: Accept merge triggers synthesis and creates resulting idea."""

    def setUp(self):
        self.idea_a = Idea.objects.create(
            owner_id=USER_A_ID, title="Image Recognition System"
        )
        self.idea_b = Idea.objects.create(
            owner_id=USER_B_ID, title="Speech Processing Pipeline"
        )
        self.merge_request = MergeRequest.objects.create(
            requesting_idea_id=self.idea_a.id,
            target_idea_id=self.idea_b.id,
            merge_type="merge",
            requested_by=USER_A_ID,
            status="pending",
            requesting_owner_consent="accepted",
            target_owner_consent="accepted",
        )

    def _execute(self):
        from apps.similarity.merge_service import execute_merge

        return execute_merge(
            merge_request_id=str(self.merge_request.id),
            requesting_idea_id=str(self.idea_a.id),
            target_idea_id=str(self.idea_b.id),
            synthesis_message=SYNTHESIS_MESSAGE,
            board_instructions=BOARD_INSTRUCTIONS,
        )

    def test_creates_merged_idea(self, mock_publish):
        """Creates new idea with 'Merged:' title prefix."""
        result = self._execute()
        merged = Idea.objects.get(id=result["resulting_idea_id"])
        assert merged.title == "Merged: Image Recognition System + Speech Processing Pipeline"
        assert merged.state == "open"
        assert merged.visibility == "collaborating"

    def test_sets_co_ownership(self, mock_publish):
        """Sets owner_id to requesting owner, co_owner_id to target owner."""
        result = self._execute()
        merged = Idea.objects.get(id=result["resulting_idea_id"])
        assert merged.owner_id == USER_A_ID
        assert merged.co_owner_id == USER_B_ID

    def test_sets_merged_from_ids(self, mock_publish):
        """Sets merged_from_idea_1_id and merged_from_idea_2_id."""
        result = self._execute()
        merged = Idea.objects.get(id=result["resulting_idea_id"])
        assert merged.merged_from_idea_1_id == self.idea_a.id
        assert merged.merged_from_idea_2_id == self.idea_b.id

    def test_creates_synthesis_chat_message(self, mock_publish):
        """Creates first chat message from merge_synthesizer agent."""
        result = self._execute()
        msg = ChatMessage.objects.filter(
            idea_id=result["resulting_idea_id"]
        ).first()
        assert msg is not None
        assert msg.sender_type == "ai"
        assert msg.ai_agent == "merge_synthesizer"
        assert msg.content == SYNTHESIS_MESSAGE

    def test_creates_board_nodes(self, mock_publish):
        """Processes board_instructions to create board nodes."""
        result = self._execute()
        nodes = BoardNode.objects.filter(
            idea_id=result["resulting_idea_id"]
        ).order_by("created_at")
        assert nodes.count() == 3
        assert nodes[0].title == "Shared Foundation"
        assert nodes[0].node_type == "group"
        assert nodes[0].created_by == "ai"
        assert nodes[1].title == "Image Recognition"
        assert nodes[1].node_type == "box"
        assert nodes[2].title == "Speech Processing"

    def test_updates_original_ideas_closed_by_merge(self, mock_publish):
        """Sets closed_by_merge_id on both original ideas."""
        result = self._execute()
        merged_id = uuid.UUID(result["resulting_idea_id"])
        self.idea_a.refresh_from_db()
        self.idea_b.refresh_from_db()
        assert self.idea_a.closed_by_merge_id == merged_id
        assert self.idea_b.closed_by_merge_id == merged_id

    def test_original_ideas_state_unchanged(self, mock_publish):
        """Original ideas retain their state (not forcefully changed)."""
        self.idea_a.state = "open"
        self.idea_a.save()
        self.idea_b.state = "rejected"
        self.idea_b.save()
        self._execute()
        self.idea_a.refresh_from_db()
        self.idea_b.refresh_from_db()
        assert self.idea_a.state == "open"
        assert self.idea_b.state == "rejected"

    def test_updates_merge_request(self, mock_publish):
        """Sets merge request status=accepted, resulting_idea_id, resolved_at."""
        result = self._execute()
        self.merge_request.refresh_from_db()
        assert self.merge_request.status == "accepted"
        assert str(self.merge_request.resulting_idea_id) == result["resulting_idea_id"]
        assert self.merge_request.resolved_at is not None

    def test_publishes_merge_complete_event(self, mock_publish):
        """Publishes merge.complete event with correct payload."""
        result = self._execute()
        mock_publish.assert_called_once()
        call_kwargs = mock_publish.call_args[1]
        assert call_kwargs["merge_request_id"] == str(self.merge_request.id)
        assert call_kwargs["resulting_idea_id"] == result["resulting_idea_id"]
        assert call_kwargs["original_idea_1_id"] == str(self.idea_a.id)
        assert call_kwargs["original_idea_2_id"] == str(self.idea_b.id)


@patch("apps.similarity.merge_service._publish_merge_complete")
class TestCollaboratorTransfer(TestCase):
    """Tests collaborator deduplication and transfer."""

    def setUp(self):
        self.idea_a = Idea.objects.create(
            owner_id=USER_A_ID, title="Idea A"
        )
        self.idea_b = Idea.objects.create(
            owner_id=USER_B_ID, title="Idea B"
        )
        self.merge_request = MergeRequest.objects.create(
            requesting_idea_id=self.idea_a.id,
            target_idea_id=self.idea_b.id,
            merge_type="merge",
            requested_by=USER_A_ID,
            status="pending",
            requesting_owner_consent="accepted",
            target_owner_consent="accepted",
        )

    def _execute(self):
        from apps.similarity.merge_service import execute_merge

        return execute_merge(
            merge_request_id=str(self.merge_request.id),
            requesting_idea_id=str(self.idea_a.id),
            target_idea_id=str(self.idea_b.id),
            synthesis_message=SYNTHESIS_MESSAGE,
            board_instructions=[],
        )

    def test_transfers_collaborators_from_both_ideas(self, mock_publish):
        """Collaborators from both ideas appear on the merged idea."""
        IdeaCollaborator.objects.create(idea=self.idea_a, user_id=COLLAB_1_ID)
        IdeaCollaborator.objects.create(idea=self.idea_b, user_id=COLLAB_2_ID)

        result = self._execute()
        collabs = set(
            IdeaCollaborator.objects.filter(
                idea_id=result["resulting_idea_id"]
            ).values_list("user_id", flat=True)
        )
        assert COLLAB_1_ID in collabs
        assert COLLAB_2_ID in collabs

    def test_deduplicates_shared_collaborators(self, mock_publish):
        """Shared collaborators appear only once on the merged idea."""
        IdeaCollaborator.objects.create(idea=self.idea_a, user_id=COLLAB_1_ID)
        IdeaCollaborator.objects.create(idea=self.idea_b, user_id=COLLAB_1_ID)
        IdeaCollaborator.objects.create(idea=self.idea_b, user_id=COLLAB_2_ID)

        result = self._execute()
        collabs = list(
            IdeaCollaborator.objects.filter(
                idea_id=result["resulting_idea_id"]
            ).values_list("user_id", flat=True)
        )
        assert len(collabs) == 2
        assert set(collabs) == {COLLAB_1_ID, COLLAB_2_ID}

    def test_excludes_owners_from_collaborators(self, mock_publish):
        """Owners (who become co-owners) are not added as collaborators."""
        IdeaCollaborator.objects.create(idea=self.idea_a, user_id=COLLAB_1_ID)
        # Owner B is a collaborator on idea A — should be excluded
        IdeaCollaborator.objects.create(idea=self.idea_a, user_id=USER_B_ID)

        result = self._execute()
        collabs = set(
            IdeaCollaborator.objects.filter(
                idea_id=result["resulting_idea_id"]
            ).values_list("user_id", flat=True)
        )
        assert COLLAB_1_ID in collabs
        assert USER_A_ID not in collabs
        assert USER_B_ID not in collabs

    def test_no_collaborators(self, mock_publish):
        """Works when neither idea has collaborators."""
        result = self._execute()
        count = IdeaCollaborator.objects.filter(
            idea_id=result["resulting_idea_id"]
        ).count()
        assert count == 0
        assert result["collaborator_ids"] == []

    def test_collaborator_ids_in_result(self, mock_publish):
        """Result includes collaborator_ids list."""
        IdeaCollaborator.objects.create(idea=self.idea_a, user_id=COLLAB_1_ID)
        IdeaCollaborator.objects.create(idea=self.idea_b, user_id=COLLAB_2_ID)
        IdeaCollaborator.objects.create(idea=self.idea_b, user_id=COLLAB_3_ID)

        result = self._execute()
        collab_id_set = {uuid.UUID(cid) for cid in result["collaborator_ids"]}
        assert collab_id_set == {COLLAB_1_ID, COLLAB_2_ID, COLLAB_3_ID}


@patch("apps.similarity.merge_service._publish_merge_complete")
class TestBoardInstructions(TestCase):
    """Tests board instruction processing."""

    def setUp(self):
        self.idea_a = Idea.objects.create(
            owner_id=USER_A_ID, title="Idea A"
        )
        self.idea_b = Idea.objects.create(
            owner_id=USER_B_ID, title="Idea B"
        )
        self.merge_request = MergeRequest.objects.create(
            requesting_idea_id=self.idea_a.id,
            target_idea_id=self.idea_b.id,
            merge_type="merge",
            requested_by=USER_A_ID,
            status="pending",
            requesting_owner_consent="accepted",
            target_owner_consent="accepted",
        )

    def _execute(self, board_instructions):
        from apps.similarity.merge_service import execute_merge

        return execute_merge(
            merge_request_id=str(self.merge_request.id),
            requesting_idea_id=str(self.idea_a.id),
            target_idea_id=str(self.idea_b.id),
            synthesis_message=SYNTHESIS_MESSAGE,
            board_instructions=board_instructions,
        )

    def test_empty_board_instructions(self, mock_publish):
        """Works with empty board instructions."""
        result = self._execute([])
        nodes = BoardNode.objects.filter(idea_id=result["resulting_idea_id"])
        assert nodes.count() == 0

    def test_skips_non_create_intents(self, mock_publish):
        """Only processes create_node/add_node intents."""
        instructions = [
            {"intent": "move_node", "target": "some-id", "position_x": 100},
            {"intent": "delete_node", "target": "some-id"},
            {"intent": "create_node", "suggested_title": "Valid Node", "suggested_content": "Content"},
        ]
        result = self._execute(instructions)
        nodes = BoardNode.objects.filter(idea_id=result["resulting_idea_id"])
        assert nodes.count() == 1
        assert nodes.first().title == "Valid Node"

    def test_board_nodes_marked_ai_created(self, mock_publish):
        """Board nodes are marked as AI-created."""
        instructions = [
            {"intent": "create_node", "suggested_title": "AI Node"},
        ]
        result = self._execute(instructions)
        node = BoardNode.objects.get(idea_id=result["resulting_idea_id"])
        assert node.created_by == "ai"
        assert node.ai_modified_indicator is True


@patch("apps.similarity.merge_service._publish_merge_complete")
class TestConsumerIntegration(TestCase):
    """T-5.5.06: Full merge flow — consumer dispatches to merge service."""

    def setUp(self):
        self.idea_a = Idea.objects.create(
            owner_id=USER_A_ID, title="Idea Alpha"
        )
        self.idea_b = Idea.objects.create(
            owner_id=USER_B_ID, title="Idea Beta"
        )
        self.merge_request = MergeRequest.objects.create(
            requesting_idea_id=self.idea_a.id,
            target_idea_id=self.idea_b.id,
            merge_type="merge",
            requested_by=USER_A_ID,
            status="pending",
            requesting_owner_consent="accepted",
            target_owner_consent="accepted",
        )
        IdeaCollaborator.objects.create(idea=self.idea_a, user_id=COLLAB_1_ID)
        IdeaCollaborator.objects.create(idea=self.idea_b, user_id=COLLAB_2_ID)

    def test_consumer_dispatches_to_merge_service(self, mock_publish):
        """handle_merge_synthesizer_complete processes event payload correctly."""
        from events.merge_consumer import handle_merge_synthesizer_complete

        payload = {
            "merge_request_id": str(self.merge_request.id),
            "requesting_idea_id": str(self.idea_a.id),
            "target_idea_id": str(self.idea_b.id),
            "synthesis_message": SYNTHESIS_MESSAGE,
            "board_instructions": BOARD_INSTRUCTIONS,
        }

        result = handle_merge_synthesizer_complete(payload)

        # Verify merged idea created
        merged = Idea.objects.get(id=result["resulting_idea_id"])
        assert merged.title == "Merged: Idea Alpha + Idea Beta"
        assert merged.owner_id == USER_A_ID
        assert merged.co_owner_id == USER_B_ID

        # Verify chat message
        msg = ChatMessage.objects.filter(idea_id=merged.id).first()
        assert msg.sender_type == "ai"
        assert msg.ai_agent == "merge_synthesizer"

        # Verify board nodes
        nodes = BoardNode.objects.filter(idea_id=merged.id)
        assert nodes.count() == 3

        # Verify collaborators transferred
        collabs = set(
            IdeaCollaborator.objects.filter(idea_id=merged.id).values_list(
                "user_id", flat=True
            )
        )
        assert COLLAB_1_ID in collabs
        assert COLLAB_2_ID in collabs

        # Verify original ideas closed
        self.idea_a.refresh_from_db()
        self.idea_b.refresh_from_db()
        assert self.idea_a.closed_by_merge_id == merged.id
        assert self.idea_b.closed_by_merge_id == merged.id

        # Verify merge request updated
        self.merge_request.refresh_from_db()
        assert self.merge_request.status == "accepted"
        assert self.merge_request.resulting_idea_id == merged.id

    def test_e2e_event_publishing(self, mock_publish):
        """T-5.5.06: merge.complete event published with all user IDs."""
        from events.merge_consumer import handle_merge_synthesizer_complete

        payload = {
            "merge_request_id": str(self.merge_request.id),
            "requesting_idea_id": str(self.idea_a.id),
            "target_idea_id": str(self.idea_b.id),
            "synthesis_message": SYNTHESIS_MESSAGE,
            "board_instructions": [],
        }

        handle_merge_synthesizer_complete(payload)

        mock_publish.assert_called_once()
        call_kwargs = mock_publish.call_args[1]
        assert call_kwargs["merge_request_id"] == str(self.merge_request.id)
        # Both owners should be in owner_ids
        owner_ids = set(call_kwargs["owner_ids"])
        assert str(USER_A_ID) in owner_ids
        assert str(USER_B_ID) in owner_ids
