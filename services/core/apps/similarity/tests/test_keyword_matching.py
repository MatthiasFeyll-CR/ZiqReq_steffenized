"""Tests for keyword matching sweep — T-5.2.01, T-5.2.02, T-5.2.03."""

import uuid
from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.utils import timezone

from apps.ideas.models import Idea
from apps.similarity.models import IdeaKeywords, MergeRequest

USER_1_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
USER_2_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")

SHARED_KEYWORDS = ["ai", "machine", "learning", "neural", "network", "deep", "model"]
UNIQUE_KEYWORDS_A = ["vision", "image", "recognition"]
UNIQUE_KEYWORDS_B = ["speech", "audio", "text"]


def _mock_get_parameter(key, default=None, cast=str):
    """Return default values for admin parameters."""
    params = {
        "min_keyword_overlap": "7",
        "similarity_time_limit": "180",
    }
    value = params.get(key)
    if value is not None:
        return cast(value)
    return default


@override_settings(DEBUG=True, AUTH_BYPASS=True)
@patch("apps.admin_config.services.get_parameter", side_effect=_mock_get_parameter)
@patch("events.publisher.publish_event")
class TestKeywordMatchingSweep(TestCase):
    """T-5.2.01, T-5.2.02, T-5.2.03: Keyword matching sweep tests."""

    def _create_idea(self, owner_id=USER_1_ID, updated_at=None, **kwargs):
        idea = Idea.objects.create(owner_id=owner_id, **kwargs)
        if updated_at:
            Idea.objects.filter(id=idea.id).update(updated_at=updated_at)
            idea.refresh_from_db()
        return idea

    def test_keyword_overlap_triggers_event(self, mock_publish, _mock_param):
        """T-5.2.01: Keyword overlap >= threshold triggers similarity.detected."""
        idea_a = self._create_idea(owner_id=USER_1_ID)
        idea_b = self._create_idea(owner_id=USER_2_ID)

        IdeaKeywords.objects.create(
            idea_id=idea_a.id,
            keywords=SHARED_KEYWORDS + UNIQUE_KEYWORDS_A,
        )
        IdeaKeywords.objects.create(
            idea_id=idea_b.id,
            keywords=SHARED_KEYWORDS + UNIQUE_KEYWORDS_B,
        )

        from apps.similarity.tasks import keyword_matching_sweep

        result = keyword_matching_sweep()

        assert result["events_published"] == 1
        mock_publish.assert_called_once()
        call_kwargs = mock_publish.call_args
        assert call_kwargs[1]["event_type"] == "similarity.detected"
        payload = call_kwargs[1]["payload"]
        assert payload["requesting_idea_id"] == str(idea_a.id)
        assert payload["target_idea_id"] == str(idea_b.id)
        assert payload["keyword_overlap_count"] == 7

    def test_below_threshold_no_event(self, mock_publish, _mock_param):
        """Keyword overlap below threshold does not trigger event."""
        idea_a = self._create_idea(owner_id=USER_1_ID)
        idea_b = self._create_idea(owner_id=USER_2_ID)

        IdeaKeywords.objects.create(
            idea_id=idea_a.id,
            keywords=SHARED_KEYWORDS[:3] + UNIQUE_KEYWORDS_A,
        )
        IdeaKeywords.objects.create(
            idea_id=idea_b.id,
            keywords=SHARED_KEYWORDS[:3] + UNIQUE_KEYWORDS_B,
        )

        from apps.similarity.tasks import keyword_matching_sweep

        result = keyword_matching_sweep()

        assert result["events_published"] == 0
        mock_publish.assert_not_called()

    def test_declined_pairs_not_rematched(self, mock_publish, _mock_param):
        """T-5.2.02: Dismissed pairs (declined merge request) are not re-matched."""
        idea_a = self._create_idea(owner_id=USER_1_ID)
        idea_b = self._create_idea(owner_id=USER_2_ID)

        IdeaKeywords.objects.create(
            idea_id=idea_a.id,
            keywords=SHARED_KEYWORDS + UNIQUE_KEYWORDS_A,
        )
        IdeaKeywords.objects.create(
            idea_id=idea_b.id,
            keywords=SHARED_KEYWORDS + UNIQUE_KEYWORDS_B,
        )

        MergeRequest.objects.create(
            requesting_idea_id=idea_a.id,
            target_idea_id=idea_b.id,
            merge_type="merge",
            requested_by=USER_1_ID,
            status="declined",
        )

        from apps.similarity.tasks import keyword_matching_sweep

        result = keyword_matching_sweep()

        assert result["events_published"] == 0
        mock_publish.assert_not_called()

    def test_time_window_filter(self, mock_publish, _mock_param):
        """T-5.2.03: Idea older than similarity_time_limit is not matched."""
        now = timezone.now()
        idea_a = self._create_idea(owner_id=USER_1_ID)
        idea_b = self._create_idea(
            owner_id=USER_2_ID,
            updated_at=now - timedelta(days=200),
        )

        IdeaKeywords.objects.create(
            idea_id=idea_a.id,
            keywords=SHARED_KEYWORDS + UNIQUE_KEYWORDS_A,
        )
        IdeaKeywords.objects.create(
            idea_id=idea_b.id,
            keywords=SHARED_KEYWORDS + UNIQUE_KEYWORDS_B,
        )

        from apps.similarity.tasks import keyword_matching_sweep

        result = keyword_matching_sweep()

        assert result["events_published"] == 0
        mock_publish.assert_not_called()

    def test_declined_reverse_pair_also_skipped(self, mock_publish, _mock_param):
        """Declined pair in reverse order is also skipped."""
        idea_a = self._create_idea(owner_id=USER_1_ID)
        idea_b = self._create_idea(owner_id=USER_2_ID)

        IdeaKeywords.objects.create(
            idea_id=idea_a.id,
            keywords=SHARED_KEYWORDS + UNIQUE_KEYWORDS_A,
        )
        IdeaKeywords.objects.create(
            idea_id=idea_b.id,
            keywords=SHARED_KEYWORDS + UNIQUE_KEYWORDS_B,
        )

        # Declined in reverse direction
        MergeRequest.objects.create(
            requesting_idea_id=idea_b.id,
            target_idea_id=idea_a.id,
            merge_type="merge",
            requested_by=USER_2_ID,
            status="declined",
        )

        from apps.similarity.tasks import keyword_matching_sweep

        result = keyword_matching_sweep()

        assert result["events_published"] == 0
        mock_publish.assert_not_called()

    def test_soft_deleted_ideas_excluded(self, mock_publish, _mock_param):
        """Soft-deleted ideas are not matched."""
        idea_a = self._create_idea(owner_id=USER_1_ID)
        idea_b = self._create_idea(owner_id=USER_2_ID, deleted_at=timezone.now())

        IdeaKeywords.objects.create(
            idea_id=idea_a.id,
            keywords=SHARED_KEYWORDS + UNIQUE_KEYWORDS_A,
        )
        IdeaKeywords.objects.create(
            idea_id=idea_b.id,
            keywords=SHARED_KEYWORDS + UNIQUE_KEYWORDS_B,
        )

        from apps.similarity.tasks import keyword_matching_sweep

        result = keyword_matching_sweep()

        assert result["events_published"] == 0
        mock_publish.assert_not_called()
