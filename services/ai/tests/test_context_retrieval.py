"""Tests for US-004: Context retrieval combines global + project_type.

Test ID: API-3.03
"""

from __future__ import annotations

import sys
from types import ModuleType
from unittest.mock import MagicMock, patch


def _make_bucket(content: str) -> MagicMock:
    bucket = MagicMock()
    bucket.content = content
    return bucket


def _setup_mock_context_models():
    """Create a mock apps.context.models module for the test environment."""
    mock_module = ModuleType("apps.context.models")
    mock_fcb = MagicMock()
    mock_fcb.DoesNotExist = type("DoesNotExist", (Exception,), {})
    mock_module.FacilitatorContextBucket = mock_fcb
    return mock_module, mock_fcb


class TestGetFacilitatorContext:
    """Test get_facilitator_context combines global + type-specific buckets."""

    def test_combines_global_and_software(self):
        """Global and software content combined with XML tags."""
        mock_module, mock_fcb = _setup_mock_context_models()
        mock_global = _make_bucket("Global guidance")
        mock_software = _make_bucket("Software guidance")

        def _get(context_type):
            return {"global": mock_global, "software": mock_software}[context_type]

        mock_fcb.objects.get.side_effect = _get

        with patch.dict(sys.modules, {"apps.context.models": mock_module}):
            # Force reimport
            import importlib

            from processing import context_assembler

            importlib.reload(context_assembler)
            result = context_assembler.get_facilitator_context("software")

        assert "<global_guidance>" in result
        assert "Global guidance" in result
        assert "<type_specific_guidance>" in result
        assert "Software guidance" in result

    def test_combines_global_and_non_software(self):
        """Global and non_software content combined."""
        mock_module, mock_fcb = _setup_mock_context_models()
        mock_global = _make_bucket("Global guidance")
        mock_ns = _make_bucket("Non-software guidance")

        def _get(context_type):
            return {"global": mock_global, "non_software": mock_ns}[context_type]

        mock_fcb.objects.get.side_effect = _get

        with patch.dict(sys.modules, {"apps.context.models": mock_module}):
            import importlib

            from processing import context_assembler

            importlib.reload(context_assembler)
            result = context_assembler.get_facilitator_context("non_software")

        assert "Global guidance" in result
        assert "Non-software guidance" in result

    def test_empty_type_bucket_returns_global_only(self):
        """When type-specific bucket is empty, only global is returned."""
        mock_module, mock_fcb = _setup_mock_context_models()
        mock_global = _make_bucket("Global guidance")
        mock_empty = _make_bucket("")

        def _get(context_type):
            return {"global": mock_global, "software": mock_empty}[context_type]

        mock_fcb.objects.get.side_effect = _get

        with patch.dict(sys.modules, {"apps.context.models": mock_module}):
            import importlib

            from processing import context_assembler

            importlib.reload(context_assembler)
            result = context_assembler.get_facilitator_context("software")

        assert "Global guidance" in result
        assert "<type_specific_guidance>" not in result

    def test_missing_buckets_returns_empty(self):
        """When both buckets are missing, returns empty string."""
        mock_module, mock_fcb = _setup_mock_context_models()
        mock_fcb.objects.get.side_effect = mock_fcb.DoesNotExist("Not found")

        with patch.dict(sys.modules, {"apps.context.models": mock_module}):
            import importlib

            from processing import context_assembler

            importlib.reload(context_assembler)
            result = context_assembler.get_facilitator_context("software")

        assert result == ""


class TestContextAssemblerWithProjectType:
    """Test ContextAssembler includes project_type in assembled context."""

    def test_assembler_includes_project_type(self):
        """Assembled context includes project_type from project data."""
        mock_module, mock_fcb = _setup_mock_context_models()
        mock_fcb.objects.get.return_value = _make_bucket("Test content")

        with patch.dict(sys.modules, {"apps.context.models": mock_module}):
            import importlib

            from processing import context_assembler

            importlib.reload(context_assembler)
            assembler = context_assembler.ContextAssembler()
            result = assembler.assemble(
                "project-1",
                {
                    "project": {
                        "title": "Test",
                        "state": "open",
                        "agent_mode": "interactive",
                        "title_manually_edited": False,
                        "project_type": "software",
                    },
                    "recent_messages": [],
                    "chat_summary": None,
                },
            )

        assert result["project_context"]["project_type"] == "software"

    def test_assembler_defaults_to_software(self):
        """When project_type missing, defaults to 'software'."""
        mock_module, mock_fcb = _setup_mock_context_models()
        mock_fcb.objects.get.return_value = _make_bucket("")

        with patch.dict(sys.modules, {"apps.context.models": mock_module}):
            import importlib

            from processing import context_assembler

            importlib.reload(context_assembler)
            assembler = context_assembler.ContextAssembler()
            result = assembler.assemble(
                "project-1",
                {
                    "project": {"title": "Test"},
                    "recent_messages": [],
                },
            )

        assert result["project_context"]["project_type"] == "software"


class TestRetrieverContextTypeFilter:
    """API-3.03: Retriever accepts project_type param for filtering."""

    def test_retrieve_method_accepts_project_type(self):
        """Retriever.retrieve() has project_type parameter."""
        import inspect

        from embedding.retriever import Retriever

        sig = inspect.signature(Retriever.retrieve)
        assert "project_type" in sig.parameters

    def test_retrieve_project_type_default_is_none(self):
        """project_type defaults to None."""
        import inspect

        from embedding.retriever import Retriever

        sig = inspect.signature(Retriever.retrieve)
        assert sig.parameters["project_type"].default is None
