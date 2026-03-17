"""Tests for US-004: Context bucket models with context_type.

Test IDs: T-3.4.01, T-3.4.02

Model field tests use gateway mirror models (apps.admin_ai_context.models)
since tests run under gateway.settings.test. The AI service's models
(apps.context.models) are structurally identical.
"""

from __future__ import annotations


class TestFacilitatorContextBucketModel:
    """T-3.4.01: Model has context_type field with correct configuration."""

    def test_context_type_field_exists(self):
        from apps.admin_ai_context.models import FacilitatorContextBucket

        field = FacilitatorContextBucket._meta.get_field("context_type")
        assert field is not None

    def test_context_type_max_length(self):
        from apps.admin_ai_context.models import FacilitatorContextBucket

        field = FacilitatorContextBucket._meta.get_field("context_type")
        assert field.max_length == 20

    def test_context_type_default_is_global(self):
        from apps.admin_ai_context.models import FacilitatorContextBucket

        field = FacilitatorContextBucket._meta.get_field("context_type")
        assert field.default == "global"

    def test_context_type_unique(self):
        from apps.admin_ai_context.models import FacilitatorContextBucket

        field = FacilitatorContextBucket._meta.get_field("context_type")
        assert field.unique is True

    def test_context_type_choices(self):
        from apps.admin_ai_context.models import FacilitatorContextBucket

        field = FacilitatorContextBucket._meta.get_field("context_type")
        values = [c[0] for c in field.choices]
        assert "global" in values
        assert "software" in values
        assert "non_software" in values


class TestContextAgentBucketModel:
    """T-3.4.01: context_agent_bucket model has context_type field."""

    def test_context_type_field_exists(self):
        from apps.admin_ai_context.models import ContextAgentBucket

        field = ContextAgentBucket._meta.get_field("context_type")
        assert field is not None

    def test_context_type_unique(self):
        from apps.admin_ai_context.models import ContextAgentBucket

        field = ContextAgentBucket._meta.get_field("context_type")
        assert field.unique is True

    def test_context_type_choices(self):
        from apps.admin_ai_context.models import ContextAgentBucket

        field = ContextAgentBucket._meta.get_field("context_type")
        values = [c[0] for c in field.choices]
        assert "global" in values
        assert "software" in values
        assert "non_software" in values
