"""Tests for vector similarity sweep — US-002."""

import uuid
from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings

from apps.ideas.models import Idea
from apps.similarity.models import MergeRequest

USER_1_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
USER_2_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")


def _mock_get_parameter(key, default=None, cast=str):
    """Return default values for admin parameters."""
    params = {
        "similarity_vector_threshold": "0.75",
        "similarity_time_limit": "180",
    }
    value = params.get(key)
    if value is not None:
        return cast(value)
    return default


@override_settings(DEBUG=True, AUTH_BYPASS=True)
@patch("apps.admin_config.services.get_parameter", side_effect=_mock_get_parameter)
@patch("events.publisher.publish_event")
class TestVectorSimilaritySweep(TestCase):
    """US-002: Vector similarity sweep tests."""

    def _create_idea(self, owner_id=USER_1_ID, **kwargs):
        return Idea.objects.create(owner_id=owner_id, **kwargs)

    def test_above_threshold_triggers_event(self, mock_publish, _mock_param):
        """Cosine similarity >= threshold triggers similarity.detected."""
        idea_a = self._create_idea(owner_id=USER_1_ID)
        idea_b = self._create_idea(owner_id=USER_2_ID)

        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            (idea_a.id, idea_b.id, 0.85),
        ]

        with patch("apps.similarity.vector_similarity.connection") as mock_conn:
            mock_conn.cursor.return_value.__enter__ = MagicMock(
                return_value=mock_cursor
            )
            mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

            from apps.similarity.vector_similarity import vector_similarity_sweep

            result = vector_similarity_sweep()

        assert result["events_published"] == 1
        mock_publish.assert_called_once()
        call_kwargs = mock_publish.call_args
        assert call_kwargs[1]["event_type"] == "similarity.detected"
        payload = call_kwargs[1]["payload"]
        assert payload["requesting_idea_id"] == str(idea_a.id)
        assert payload["target_idea_id"] == str(idea_b.id)
        assert payload["similarity_score"] == 0.85

    def test_below_threshold_no_event(self, mock_publish, _mock_param):
        """No rows returned from SQL means no events published."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []

        with patch("apps.similarity.vector_similarity.connection") as mock_conn:
            mock_conn.cursor.return_value.__enter__ = MagicMock(
                return_value=mock_cursor
            )
            mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

            from apps.similarity.vector_similarity import vector_similarity_sweep

            result = vector_similarity_sweep()

        assert result["events_published"] == 0
        mock_publish.assert_not_called()

    def test_declined_pairs_excluded(self, mock_publish, _mock_param):
        """Declined merge request pair is excluded from results."""
        idea_a = self._create_idea(owner_id=USER_1_ID)
        idea_b = self._create_idea(owner_id=USER_2_ID)

        MergeRequest.objects.create(
            requesting_idea_id=idea_a.id,
            target_idea_id=idea_b.id,
            merge_type="merge",
            requested_by=USER_1_ID,
            status="declined",
        )

        # SQL returns the pair, but task should filter it out
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            (idea_a.id, idea_b.id, 0.90),
        ]

        with patch("apps.similarity.vector_similarity.connection") as mock_conn:
            mock_conn.cursor.return_value.__enter__ = MagicMock(
                return_value=mock_cursor
            )
            mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

            from apps.similarity.vector_similarity import vector_similarity_sweep

            result = vector_similarity_sweep()

        assert result["events_published"] == 0
        mock_publish.assert_not_called()

    def test_declined_reverse_pair_excluded(self, mock_publish, _mock_param):
        """Declined pair in reverse order is also excluded."""
        idea_a = self._create_idea(owner_id=USER_1_ID)
        idea_b = self._create_idea(owner_id=USER_2_ID)

        # Declined in reverse direction
        MergeRequest.objects.create(
            requesting_idea_id=idea_b.id,
            target_idea_id=idea_a.id,
            merge_type="merge",
            requested_by=USER_2_ID,
            status="declined",
        )

        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            (idea_a.id, idea_b.id, 0.88),
        ]

        with patch("apps.similarity.vector_similarity.connection") as mock_conn:
            mock_conn.cursor.return_value.__enter__ = MagicMock(
                return_value=mock_cursor
            )
            mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

            from apps.similarity.vector_similarity import vector_similarity_sweep

            result = vector_similarity_sweep()

        assert result["events_published"] == 0
        mock_publish.assert_not_called()

    def test_multiple_matches(self, mock_publish, _mock_param):
        """Multiple pairs above threshold each get an event."""
        idea_a = self._create_idea(owner_id=USER_1_ID)
        idea_b = self._create_idea(owner_id=USER_2_ID)
        idea_c = self._create_idea(owner_id=USER_2_ID)

        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            (idea_a.id, idea_b.id, 0.80),
            (idea_a.id, idea_c.id, 0.92),
        ]

        with patch("apps.similarity.vector_similarity.connection") as mock_conn:
            mock_conn.cursor.return_value.__enter__ = MagicMock(
                return_value=mock_cursor
            )
            mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

            from apps.similarity.vector_similarity import vector_similarity_sweep

            result = vector_similarity_sweep()

        assert result["events_published"] == 2
        assert mock_publish.call_count == 2

    def test_payload_includes_similarity_score(self, mock_publish, _mock_param):
        """Event payload contains similarity_score rounded to 4 decimals."""
        idea_a = self._create_idea(owner_id=USER_1_ID)
        idea_b = self._create_idea(owner_id=USER_2_ID)

        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            (idea_a.id, idea_b.id, 0.876543),
        ]

        with patch("apps.similarity.vector_similarity.connection") as mock_conn:
            mock_conn.cursor.return_value.__enter__ = MagicMock(
                return_value=mock_cursor
            )
            mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

            from apps.similarity.vector_similarity import vector_similarity_sweep

            result = vector_similarity_sweep()

        assert result["events_published"] == 1
        payload = mock_publish.call_args[1]["payload"]
        assert payload["similarity_score"] == 0.8765
